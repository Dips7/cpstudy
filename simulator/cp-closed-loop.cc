// Closed-loop research model for ns-3.46.1. 802.11p PHY/AdhocWifiMac;
// not an ITS-G5, CPM ASN.1, certificate, or perception-accuracy implementation.
#include "ns3/core-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/network-module.h"
#include "ns3/wifi-module.h"
#include <algorithm>
#include <cmath>
#include <deque>
#include <fstream>
#include <iomanip>
#include <map>
#include <vector>
using namespace ns3;

class StudyHeader : public Header {
public:
    uint32_t source=0, sequence=0, kind=0, backlog=0;
    uint64_t acquired=0;
    static TypeId GetTypeId() {
        static TypeId id=TypeId("StudyHeader").SetParent<Header>().AddConstructor<StudyHeader>();
        return id;
    }
    TypeId GetInstanceTypeId() const override { return GetTypeId(); }
    uint32_t GetSerializedSize() const override { return 24; }
    void Serialize(Buffer::Iterator i) const override {
        i.WriteHtonU32(source);i.WriteHtonU32(sequence);i.WriteHtonU64(acquired);
        i.WriteHtonU32(kind);i.WriteHtonU32(backlog);
    }
    uint32_t Deserialize(Buffer::Iterator i) override {
        source=i.ReadNtohU32();sequence=i.ReadNtohU32();acquired=i.ReadNtohU64();
        kind=i.ReadNtohU32();backlog=i.ReadNtohU32();return 24;
    }
    void Print(std::ostream& os) const override { os<<source<<":"<<sequence; }
};

struct State {
    Ptr<Socket> send;
    Ptr<WifiPhy> phy;
    std::deque<StudyHeader> queue;
    bool active=false;
    double rate=10, due=0, phase=0;
    uint32_t lowStreak=0,feedbackSequence=0;
    double dccDelta=.005,dccEstimate=0,dccPrevious=0;
    double initialCoordinate=0,lane=0;
    int direction=1;
    bool horizontal=true;
    // Feedback becomes observable only after its verification completes.
    std::map<uint32_t,std::pair<int64_t,uint32_t>> feedback;
    std::vector<std::pair<int64_t,int64_t>> busy;
    int64_t lastStateEnd=0;
};

static uint32_t n=10,seed=1,queueCapacity=32,payload=1100,security=100,feedbackBytes=96;
static double duration=10,warmup=2,opportunityHz=10,maxRate=10,minRate=1,deadlineMs=100;
static double inferenceMs=10,signMs=1,verifyMs=1,fusionMs=2,controlMs=100,feedbackMs=200;
static double staleMs=600,radioHigh=.65,radioLow=.4,queueHigh=8,queueLow=2,decrease=.8,increase=.5;
static double serviceCv=0,rangeM=150,speed=10;
static std::string policy="fixed",scenario="intersection",output=".";
static bool matchedFeedback=false;
static NodeContainer nodes;
static std::vector<State> states;
static std::ofstream events,opportunities,controls,positions,dccTrace;
static uint64_t traceOrder=0;

static uint32_t Depth(uint32_t r) { return states[r].queue.size()+uint32_t(states[r].active); }
static void LogEvent(std::string event,uint32_t receiver,const StudyHeader& h,std::string reason="") {
    events<<Simulator::Now().GetNanoSeconds()<<','<<event<<','<<h.source<<','<<receiver<<','
          <<h.sequence<<','<<h.kind<<','<<h.acquired<<','<<Depth(receiver)<<','<<reason<<','
          <<h.backlog<<','<<traceOrder++<<'\n';
}

static uint64_t Mix(uint64_t v) {
    v+=0x9e3779b97f4a7c15ULL;v=(v^(v>>30))*0xbf58476d1ce4e5b9ULL;
    v=(v^(v>>27))*0x94d049bb133111ebULL;return v^(v>>31);
}
static double ServiceMs(uint32_t receiver,const StudyHeader& h) {
    if(serviceCv==0 || verifyMs==0)return verifyMs;
    uint64_t key=Mix(seed)^Mix(receiver+1000)^Mix(h.source+2000)^Mix(h.sequence+3000)^Mix(h.kind+4000);
    double u=(double(Mix(key)>>11)+.5)/9007199254740992.0;
    double v=(double(Mix(key+1)>>11)+.5)/9007199254740992.0;
    double z=std::sqrt(-2*std::log(u))*std::cos(2*3.141592653589793*v);
    double sigma=std::sqrt(std::log1p(serviceCv*serviceCv));
    return verifyMs*std::exp(sigma*z-sigma*sigma/2);
}
static void Ready(uint32_t r,StudyHeader h) {
    if(Simulator::Now().GetNanoSeconds()>int64_t(h.acquired)+int64_t(deadlineMs*1e6))
        LogEvent("terminal",r,h,"fusion_expired");
    else { LogEvent("fusion_ready",r,h);LogEvent("terminal",r,h,"success"); }
}
static void Start(uint32_t r,StudyHeader h);
static void Verified(uint32_t r,StudyHeader h) {
    LogEvent("verification_end",r,h);
    if(h.kind==1) {
        // Use acquisition time, not receive/verify time, for feedback age.
        auto& table=states[r].feedback;
        auto found=table.find(h.source);
        if(found==table.end() || int64_t(h.acquired)>found->second.first)
            table[h.source]={int64_t(h.acquired),h.backlog};
        LogEvent("terminal",r,h,"feedback_ready");
    } else if(Simulator::Now().GetNanoSeconds()>int64_t(h.acquired)+int64_t(deadlineMs*1e6))
        LogEvent("terminal",r,h,"verification_expired");
    else Simulator::Schedule(MilliSeconds(fusionMs),&Ready,r,h);
    states[r].active=false;
    if(!states[r].queue.empty()) {
        auto next=states[r].queue.front();states[r].queue.pop_front();Start(r,next);
    }
}
static void Start(uint32_t r,StudyHeader h) {
    states[r].active=true;LogEvent("verification_start",r,h);
    Simulator::Schedule(Seconds(ServiceMs(r,h)/1000),&Verified,r,h);
}
static void Receive(uint32_t r,Ptr<Socket> socket) {
    while(auto packet=socket->Recv()) {
        StudyHeader h;
        if(packet->GetSize()<h.GetSerializedSize())continue;
        packet->RemoveHeader(h);
        if(h.source==r || h.source>=n)continue;
        LogEvent("reception",r,h);
        if(!states[r].active)Start(r,h);
        else if(states[r].queue.size()>=queueCapacity)LogEvent("terminal",r,h,"queue_overflow");
        else {states[r].queue.push_back(h);LogEvent("enqueue",r,h);}
    }
}
static void Send(uint32_t source,StudyHeader h) {
    uint32_t size=h.kind ? feedbackBytes+security : payload+security;
    auto packet=Create<Packet>(size-h.GetSerializedSize());packet->AddHeader(h);
    auto result=states[source].send->Send(packet);
    LogEvent("transmission",source,h,result>=0 ? "accepted_by_socket" : "socket_rejected");
}
static Vector Location(uint32_t node) {
    // Ground-truth evaluation geometry is a pure function of the exogenous
    // trajectory and time, independent of radio-triggered mobility queries.
    auto& s=states[node];double half=scenario=="highway" ? 600 : 300;
    double x=std::fmod(s.initialCoordinate+s.direction*speed*Simulator::Now().GetSeconds()+half,2*half);
    if(x<0)x+=2*half;x-=half;
    return s.horizontal ? Vector(x,s.lane,1.5) : Vector(s.lane,x,1.5);
}
static bool InRegion(const Vector& p) {
    return scenario=="highway" ? std::abs(p.x)<=300 : (std::abs(p.x)<=150 && std::abs(p.y)<=150);
}
static void Acquire(uint32_t source,uint32_t sequence) {
    int64_t now=Simulator::Now().GetNanoSeconds();auto& s=states[source];
    double seconds=Simulator::Now().GetSeconds();
    bool selected=seconds+1e-9>=s.due;
    if(selected) {
        if(policy=="dcc")s.due=seconds+1/s.rate; // single-service minimum-gap gate
        else s.due+=1/s.rate; // average-rate target; <= one sensing-tick jitter
    }
    Vector p=Location(source);
    opportunities<<source<<','<<sequence<<','<<now<<','<<now+int64_t(deadlineMs*1e6)<<','
                 <<selected<<','<<p.x<<','<<p.y<<',';
    if(InRegion(p))for(uint32_t r=0;r<n;++r)if(r!=source) {
        auto q=Location(r);
        if(InRegion(q) && CalculateDistance(p,q)<=rangeM)opportunities<<r<<'|';
    }
    opportunities<<','<<traceOrder++<<'\n';
    if(selected) {
        StudyHeader h;h.source=source;h.sequence=sequence;h.acquired=now;
        Simulator::Schedule(MilliSeconds(inferenceMs+signMs),&Send,source,h);
    }
    double next=s.phase+(sequence+1)/opportunityHz;
    if(next<duration)Simulator::Schedule(Seconds(next-seconds),&Acquire,source,sequence+1);
}
static void PhyState(uint32_t node,Time start,Time span,WifiPhyState state) {
    auto a=start.GetNanoSeconds(),b=(start+span).GetNanoSeconds();
    states[node].lastStateEnd=std::max(states[node].lastStateEnd,b);
    if(state==WifiPhyState::TX || state==WifiPhyState::RX || state==WifiPhyState::CCA_BUSY)
        states[node].busy.emplace_back(a,b);
}
static double Busy(uint32_t node,double intervalMs=controlMs) {
    auto& s=states[node];int64_t now=Simulator::Now().GetNanoSeconds();
    int64_t begin=std::max(int64_t(0),now-int64_t(intervalMs*1e6));
    s.busy.erase(std::remove_if(s.busy.begin(),s.busy.end(),[begin](auto x){return x.second<=begin;}),s.busy.end());
    std::vector<std::pair<int64_t,int64_t>> intervals=s.busy;
    // Trace RX/CCA intervals are finalized at transitions. Include the ongoing
    // state only from the last known endpoint, avoiding double counting TX.
    if(!s.phy->IsStateIdle() && s.lastStateEnd<now)intervals.emplace_back(s.lastStateEnd,now);
    std::sort(intervals.begin(),intervals.end());int64_t busy=0,cursor=begin;
    for(auto x:intervals) {auto a=std::max({begin,x.first,cursor}),b=std::min(now,x.second);
        if(b>a){busy+=b-a;cursor=b;}}
    return now>begin ? double(busy)/(now-begin) : 0;
}
static void Control(uint32_t node) {
    auto& s=states[node];double busy=Busy(node),backlog=0,sumBacklog=0;
    int64_t now=Simulator::Now().GetNanoSeconds();uint32_t observed=0;
    for(auto item:s.feedback)if(now-item.second.first<=int64_t(staleMs*1e6)) {
        backlog=std::max(backlog,double(item.second.second));
        sumBacklog+=double(item.second.second);
        ++observed;
    }
    double avgBacklog = observed>0 ? (sumBacklog / observed) : 0;
    bool stale=observed==0,useRadio=policy=="radio" || policy=="joint" || policy=="calibrated",useQueue=policy=="receiver" || policy=="joint" || policy=="calibrated";
    if(policy=="calibrated") {
        bool qHigh = (observed > 0) && (avgBacklog > queueHigh);
        bool qLow = (observed == 0) || (avgBacklog < queueLow);
        bool rHigh = busy > radioHigh;
        bool rLow = busy < radioLow;
        bool high = rHigh || qHigh;
        bool low = rLow && qLow;
        if(high){s.rate=std::max(minRate,s.rate*decrease);s.lowStreak=0;}
        else if(low){if(++s.lowStreak>=2){s.rate=std::min(maxRate,s.rate+increase);s.lowStreak=0;}}
        else s.lowStreak=0;
    } else if(policy!="fixed" && policy!="dcc") {
        bool high=(useRadio && busy>radioHigh)||(useQueue && (stale || backlog>queueHigh));
        bool low=(!useRadio || busy<radioLow)&&(!useQueue || (!stale && backlog<queueLow));
        if(high){s.rate=std::max(minRate,s.rate*decrease);s.lowStreak=0;}
        else if(low){if(++s.lowStreak>=2){s.rate=std::min(maxRate,s.rate+increase);s.lowStreak=0;}}
        else s.lowStreak=0;
    }
    controls<<now<<','<<node<<','<<s.rate<<','<<busy<<','<<backlog<<','<<stale<<','<<observed<<','<<traceOrder++<<'\n';
    if(Simulator::Now().GetSeconds()+controlMs/1000<duration)
        Simulator::Schedule(MilliSeconds(controlMs),&Control,node);
}
static double DataAirtime() {
    return .00004+.000008*std::ceil((22+8*double(payload+security+64))/48);
}
static void DccSample(uint32_t node,uint32_t tick) {
    auto& s=states[node];double current=Busy(node,100);
    if(tick%2==0) {
        s.dccEstimate=.5*s.dccEstimate+.25*(current+s.dccPrevious);
        double offset=std::clamp(.0012*(.68-s.dccEstimate),-.00025,.0005);
        s.dccDelta=std::clamp(.984*s.dccDelta+offset,.0006,.03);
        double gap=std::clamp(DataAirtime()/s.dccDelta,.025,1.);
        s.rate=std::min(maxRate,1/gap);
        dccTrace<<Simulator::Now().GetNanoSeconds()<<','<<node<<','<<current<<','<<s.dccPrevious<<','
                <<s.dccEstimate<<','<<s.dccDelta<<','<<s.rate<<','<<traceOrder++<<'\n';
    }
    s.dccPrevious=current;
    if(Simulator::Now().GetSeconds()+.1<duration)Simulator::Schedule(Seconds(.1),&DccSample,node,tick+1);
}
static void Feedback(uint32_t node) {
    StudyHeader h;h.source=node;h.sequence=states[node].feedbackSequence++;h.kind=1;
    h.acquired=Simulator::Now().GetNanoSeconds();h.backlog=Depth(node);
    LogEvent("feedback_acquisition",node,h);
    Simulator::Schedule(MilliSeconds(signMs),&Send,node,h);
    if(Simulator::Now().GetSeconds()+feedbackMs/1000<duration)
        Simulator::Schedule(MilliSeconds(feedbackMs),&Feedback,node);
}
static void Move(uint32_t node,double coordinate,int direction,bool horizontal,double lane) {
    double half=scenario=="intersection" ? 300 : 600;
    auto model=nodes.Get(node)->GetObject<ConstantVelocityMobilityModel>();
    model->SetPosition(horizontal ? Vector(coordinate,lane,1.5) : Vector(lane,coordinate,1.5));
    model->SetVelocity(horizontal ? Vector(direction*speed,0,0) : Vector(0,direction*speed,0));
    positions<<Simulator::Now().GetNanoSeconds()<<','<<node<<','<<model->GetPosition().x<<','<<model->GetPosition().y<<'\n';
    double boundary=direction>0 ? half : -half;
    double travel=std::abs(boundary-coordinate)/speed;
    if(Simulator::Now().GetSeconds()+travel<duration)
        Simulator::Schedule(Seconds(travel),&Move,node,-boundary,direction,horizontal,lane);
}

int main(int argc,char** argv) {
    CommandLine cmd;
    cmd.AddValue("sources","Vehicles",n);cmd.AddValue("seed","RNG run",seed);
    cmd.AddValue("duration_s","Duration",duration);cmd.AddValue("warmup_s","Warmup",warmup);
    cmd.AddValue("opportunity_hz","Acquisition Hz",opportunityHz);cmd.AddValue("max_rate_hz","Max emission",maxRate);
    cmd.AddValue("min_rate_hz","Min emission",minRate);cmd.AddValue("deadline_ms","Deadline",deadlineMs);
    cmd.AddValue("inference_ms","Inference",inferenceMs);cmd.AddValue("sign_ms","Signing",signMs);
    cmd.AddValue("verify_ms","Verification",verifyMs);cmd.AddValue("fusion_ms","Fusion availability",fusionMs);
    cmd.AddValue("queue_capacity","Waiting capacity",queueCapacity);cmd.AddValue("payload_bytes","Payload",payload);
    cmd.AddValue("security_bytes","Security overhead",security);cmd.AddValue("feedback_bytes","Feedback payload",feedbackBytes);
    cmd.AddValue("control_ms","Control interval",controlMs);cmd.AddValue("feedback_ms","Feedback interval",feedbackMs);
    cmd.AddValue("feedback_stale_ms","Feedback staleness",staleMs);cmd.AddValue("radio_high","High occupancy",radioHigh);
    cmd.AddValue("radio_low","Low occupancy",radioLow);cmd.AddValue("queue_high","High queue",queueHigh);
    cmd.AddValue("queue_low","Low queue",queueLow);cmd.AddValue("decrease","Multiplicative decrease",decrease);
    cmd.AddValue("increase_hz","Additive increase",increase);cmd.AddValue("service_cv","Service CV",serviceCv);
    cmd.AddValue("range_m","Eligibility radius",rangeM);cmd.AddValue("speed_mps","Vehicle speed",speed);
    cmd.AddValue("policy","Policy",policy);cmd.AddValue("scenario","Scenario",scenario);
    cmd.AddValue("matched_feedback","Feedback in all baselines",matchedFeedback);cmd.AddValue("output","Output directory",output);
    cmd.Parse(argc,argv);
    NS_ABORT_MSG_IF(n<2 || n>1000 || speed<=0 || feedbackBytes+security<24 || payload+security<24,"Invalid input");
    RngSeedManager::SetSeed(1);RngSeedManager::SetRun(seed);
    events.open(output+"/network-events.csv");opportunities.open(output+"/network-opportunities.csv");
    controls.open(output+"/network-controls.csv");positions.open(output+"/network-positions.csv");
    dccTrace.open(output+"/network-dcc.csv");
    NS_ABORT_MSG_IF(!events || !opportunities || !controls || !positions || !dccTrace,"Output open failed");
    events<<"event_ns,event_type,source_id,receiver_id,sequence,kind,acquisition_ns,queue_depth,reason,reported_backlog,trace_order\n";
    opportunities<<"source_id,sequence,acquisition_ns,deadline_ns,generated,x,y,receiver_ids,trace_order\n";
    controls<<"event_ns,node_id,rate_hz,busy_fraction,remote_backlog,feedback_stale,observed_neighbors,trace_order\n";
    positions<<"event_ns,node_id,x,y\n";controls<<std::setprecision(15);opportunities<<std::setprecision(15);
    dccTrace<<"event_ns,node_id,current_busy,previous_busy,smoothed_busy,delta,rate_hz,trace_order\n"<<std::setprecision(15);
    nodes.Create(n);states.resize(n);
    MobilityHelper mobility;mobility.SetMobilityModel("ns3::ConstantVelocityMobilityModel");mobility.Install(nodes);
    WifiHelper wifi;wifi.SetStandard(WIFI_STANDARD_80211p);
    wifi.SetRemoteStationManager("ns3::ConstantRateWifiManager","DataMode",StringValue("OfdmRate6MbpsBW10MHz"),
        "ControlMode",StringValue("OfdmRate6MbpsBW10MHz"),"NonUnicastMode",StringValue("OfdmRate6MbpsBW10MHz"));
    YansWifiChannelHelper channel;channel.SetPropagationDelay("ns3::ConstantSpeedPropagationDelayModel");
    channel.AddPropagationLoss("ns3::LogDistancePropagationLossModel","Exponent",DoubleValue(2.5),"ReferenceLoss",DoubleValue(47.86));
    YansWifiPhyHelper phy;phy.SetChannel(channel.Create());
    phy.Set("ChannelSettings",StringValue("{172, 10, BAND_5GHZ, 0}"));
    phy.Set("TxPowerStart",DoubleValue(23));phy.Set("TxPowerEnd",DoubleValue(23));
    WifiMacHelper mac;mac.SetType("ns3::AdhocWifiMac");auto devices=wifi.Install(phy,mac,nodes);
    wifi.AssignStreams(devices,1);
    InternetStackHelper internet;internet.Install(nodes);Ipv4AddressHelper address;
    address.SetBase("10.1.0.0","255.255.0.0");address.Assign(devices);
    auto phases=CreateObject<UniformRandomVariable>();phases->SetStream(10000);
    auto locations=CreateObject<UniformRandomVariable>();locations->SetStream(20000);
    for(uint32_t i=0;i<n;++i) {
        auto& s=states[i];s.rate=maxRate;s.phase=phases->GetValue(0,1/opportunityHz);s.due=s.phase;
        if(policy=="dcc")s.rate=std::min(maxRate,1/std::clamp(DataAirtime()/s.dccDelta,.025,1.));
        s.phy=DynamicCast<WifiNetDevice>(devices.Get(i))->GetPhy();
        s.phy->GetState()->TraceConnectWithoutContext("State",MakeBoundCallback(&PhyState,i));
        auto receive=Socket::CreateSocket(nodes.Get(i),UdpSocketFactory::GetTypeId());
        receive->Bind(InetSocketAddress(Ipv4Address::GetAny(),9000));receive->SetRecvCallback(MakeBoundCallback(&Receive,i));
        s.send=Socket::CreateSocket(nodes.Get(i),UdpSocketFactory::GetTypeId());s.send->SetAllowBroadcast(true);
        s.send->Connect(InetSocketAddress(Ipv4Address("10.1.255.255"),9000));
        int direction=i%2 ? -1 : 1;bool horizontal=scenario=="highway" || i%4<2;
        double lane=(i%2 ? -1 : 1)*(1.75+3.5*(scenario=="highway" ? (i/2)%3 : 0));
        double half=scenario=="highway" ? 600 : 300;
        s.initialCoordinate=locations->GetValue(-half,half);s.direction=direction;
        s.horizontal=horizontal;s.lane=lane;
        Move(i,s.initialCoordinate,direction,horizontal,lane);
        Simulator::Schedule(Seconds(s.phase),&Acquire,i,0);
        Simulator::Schedule(Seconds(s.phase+controlMs/1000),&Control,i);
        if(policy=="dcc")Simulator::Schedule(Seconds(.1),&DccSample,i,1);
        if(policy=="receiver" || policy=="joint" || policy=="calibrated" || matchedFeedback)
            Simulator::Schedule(Seconds(s.phase),&Feedback,i);
    }
    Simulator::Stop(Seconds(duration));Simulator::Run();Simulator::Destroy();
    events.close();opportunities.close();controls.close();positions.close();dccTrace.close();
    std::cout<<"Closed-loop simulation finished\n";
}
