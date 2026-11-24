// ns-3.46.1 pilot: 802.11p PHY with AdhocWifiMac, UDP broadcast.
// Not a complete ITS-G5/GeoNetworking/BTP/CPS implementation.
#include "ns3/applications-module.h"
#include "ns3/core-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/network-module.h"
#include "ns3/wifi-module.h"
#include <fstream>
#include <iomanip>
using namespace ns3;

static std::ofstream events;
static uint32_t bytes = 1200;
static uint32_t count = 0;
static double rate = 10;
static double duration = 10;
static uint64_t received = 0;

static void Receive(uint32_t receiver, Ptr<Socket> socket)
{
    while (auto packet = socket->Recv())
    {
        SeqTsHeader h;
        packet->RemoveHeader(h);
        uint32_t sender = h.GetSeq() / 1000000;
        uint32_t sequence = h.GetSeq() % 1000000;
        events << Simulator::Now().GetNanoSeconds() << ",rx," << sender << ','
               << receiver << ',' << sequence << ',' << bytes << '\n';
        ++received;
    }
}

static void Send(Ptr<Socket> socket, uint32_t sender, uint32_t sequence)
{
    SeqTsHeader h;
    h.SetSeq(sender * 1000000 + sequence);
    auto packet = Create<Packet>(bytes - h.GetSerializedSize());
    packet->AddHeader(h);
    socket->Send(packet);
    events << Simulator::Now().GetNanoSeconds() << ",send," << sender << ",-1,"
           << sequence << ',' << bytes << '\n';
    if (Simulator::Now().GetSeconds() + 1/rate < duration)
        Simulator::Schedule(Seconds(1/rate), &Send, socket, sender, sequence+1);
}

int main(int argc, char** argv)
{
    uint32_t seed = 1;
    count = 10;
    std::string output = "radio-pilot.csv";
    CommandLine cmd;
    cmd.AddValue("sources", "Number of vehicles", count);
    cmd.AddValue("duration", "Duration seconds", duration);
    cmd.AddValue("rate", "Broadcast Hz", rate);
    cmd.AddValue("bytes", "UDP payload bytes including sequence header", bytes);
    cmd.AddValue("seed", "RNG run index", seed);
    cmd.AddValue("output", "Event CSV", output);
    cmd.Parse(argc,argv);
    NS_ABORT_MSG_IF(count < 2 || count > 1000 || rate <= 0 || duration <= 0 || bytes < 12,
                    "Invalid pilot settings");
    RngSeedManager::SetSeed(1);
    RngSeedManager::SetRun(seed);
    events.open(output);
    NS_ABORT_MSG_IF(!events, "Cannot open event output");
    events << "event_ns,event_type,source_id,receiver_id,sequence,payload_bytes\n";
    NodeContainer nodes;
    nodes.Create(count);
    auto positions = CreateObject<ListPositionAllocator>();
    for(uint32_t i=0;i<count;++i)
        positions->Add(Vector(10.0*(i%10),10.0*(i/10),1.5));
    MobilityHelper mobility;
    mobility.SetPositionAllocator(positions);
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(nodes);
    WifiHelper wifi;
    wifi.SetStandard(WIFI_STANDARD_80211p);
    wifi.SetRemoteStationManager("ns3::ConstantRateWifiManager",
        "DataMode",StringValue("OfdmRate6MbpsBW10MHz"),
        "ControlMode",StringValue("OfdmRate6MbpsBW10MHz"),
        "NonUnicastMode",StringValue("OfdmRate6MbpsBW10MHz"));
    YansWifiChannelHelper channel;
    channel.SetPropagationDelay("ns3::ConstantSpeedPropagationDelayModel");
    channel.AddPropagationLoss("ns3::LogDistancePropagationLossModel",
        "Exponent",DoubleValue(2.5),"ReferenceLoss",DoubleValue(47.86));
    YansWifiPhyHelper phy;
    phy.SetChannel(channel.Create());
    phy.Set("ChannelSettings",StringValue("{172, 10, BAND_5GHZ, 0}"));
    phy.Set("TxPowerStart",DoubleValue(23));
    phy.Set("TxPowerEnd",DoubleValue(23));
    WifiMacHelper mac;
    mac.SetType("ns3::AdhocWifiMac");
    auto devices = wifi.Install(phy,mac,nodes);
    wifi.AssignStreams(devices,1);
    InternetStackHelper internet;
    internet.Install(nodes);
    Ipv4AddressHelper addresses;
    addresses.SetBase("10.1.0.0","255.255.0.0");
    addresses.Assign(devices);
    auto phase=CreateObject<UniformRandomVariable>();
    phase->SetStream(10000);
    for(uint32_t i=0;i<count;++i)
    {
        auto receive=Socket::CreateSocket(nodes.Get(i),UdpSocketFactory::GetTypeId());
        receive->Bind(InetSocketAddress(Ipv4Address::GetAny(),9000));
        receive->SetRecvCallback(MakeBoundCallback(&Receive,i));
        auto send=Socket::CreateSocket(nodes.Get(i),UdpSocketFactory::GetTypeId());
        send->SetAllowBroadcast(true);
        send->Connect(InetSocketAddress(Ipv4Address("10.1.255.255"),9000));
        // Acquisition precedes radio generation by 11 ms in this pilot.
        Simulator::Schedule(Seconds(0.011+phase->GetValue(0,1/rate)),&Send,send,i,0);
    }
    Simulator::Stop(Seconds(duration+0.1));
    Simulator::Run();
    Simulator::Destroy();
    events.close();
    std::cout << "Received message-receiver pairs: " << received << std::endl;
}
