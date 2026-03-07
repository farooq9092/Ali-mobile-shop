import streamlit as st
from graphviz import Digraph
import time
import random

st.set_page_config(page_title="TCP/IP + OSI Simulator v3.1", layout="wide")
st.title("🌐 TCP/IP + OSI Advanced Simulator v3.1")
st.write("Interactive Lab Simulator: Sender → Routers → Receiver or OSI Model View")

# Sidebar
st.sidebar.header("Simulation Options")
sim_type = st.sidebar.selectbox("Choose Simulator", ["TCP/IP Simulation", "OSI Model Simulation"])
protocol = st.sidebar.selectbox("Transport Protocol", ["TCP", "UDP"])
message = st.sidebar.text_input("Enter Message", "Hello World")
src_ip = st.sidebar.text_input("Source IP", "192.168.1.10")
dst_ip = st.sidebar.text_input("Destination IP", "192.168.1.20")
src_port = st.sidebar.text_input("Source Port", "5000")
dst_port = st.sidebar.text_input("Destination Port", "80")
simulate = st.sidebar.button("Start Simulation")

routers = ["Router1", "Router2"]
delay = st.sidebar.slider("Network Delay (sec)", 0.0, 3.0, 1.0)
loss = st.sidebar.slider("Packet Loss (%)", 0, 50, 0)

# ----------------------------
# Helper Functions
# ----------------------------
def encapsulate(data):
    if protocol == "TCP":
        transport = f"TCP(src={src_port}, dst={dst_port})[{data}]"
    else:
        transport = f"UDP(src={src_port}, dst={dst_port})[{data}]"
    internet = f"IP(src={src_ip}, dst={dst_ip})[{transport}]"
    network_access = f"ETH_FRAME[{internet}]"
    return data, transport, internet, network_access

def network_diagram(packet_stage=None):
    g = Digraph()
    g.node("A", "Sender")
    for r in routers:
        g.node(r, r)
    g.node("B", "Receiver")
    g.edge("A", routers[0], label=packet_stage or "Packet")
    for i in range(len(routers)-1):
        g.edge(routers[i], routers[i+1], label=packet_stage or "Forward")
    g.edge(routers[-1], "B", label=packet_stage or "Forward")
    return g

# ----------------------------
# OSI Model Simulator
# ----------------------------
def osi_model_simulator():
    st.subheader("🌐 OSI Model Simulation")
    app, transport, internet, frame = encapsulate(message)
    osi_encap = {
        "Application": app,
        "Presentation": f"[Format]{app}",
        "Session": f"[Session]{app}",
        "Transport": transport,
        "Network": internet,
        "Data Link": frame,
        "Physical": "Bits transmitted over medium"
    }
    st.write("**Encapsulation**")
    for layer, val in osi_encap.items():
        st.write(f"**{layer} Layer** → {val}")

    st.write("---")
    st.write("**Decapsulation**")
    try:
        step1 = frame.replace("ETH_FRAME[", "").rstrip("]")
        step2 = step1.split("[",1)[1].rstrip("]") if "[" in step1 else step1
        step3 = step2.split("[",1)[1].rstrip("]") if "[" in step2 else step2
        st.success("Application Received Message: " + step3)
        osi_decaps = {
            "Physical Layer": "Bits received from medium",
            "Data Link Layer": f"ETH_FRAME stripped → {step1}",
            "Network Layer": f"IP Header stripped → {step2}",
            "Transport Layer": f"{protocol} Header stripped → {step3}",
            "Session Layer": "[Session info processed]",
            "Presentation Layer": "[Data format converted]",
            "Application Layer": step3
        }
        for layer, val in osi_decaps.items():
            st.write(f"**{layer} Layer** → {val}")
    except Exception as e:
        st.error("Error during decapsulation: " + str(e))

# ----------------------------
# TCP/IP Simulation
# ----------------------------
def tcp_ip_simulator():
    st.subheader("🌐 TCP/IP Packet Flow Simulation")
    app, transport, internet, frame = encapsulate(message)

    # Encapsulation display
    st.write("**Encapsulation Process**")
    col1, col2, col3, col4 = st.columns(4)
    col1.write(f"Application Layer → {app}")
    col2.write(f"Transport Layer → {transport}")
    col3.write(f"Internet Layer → {internet}")
    col4.write(f"Network Access Layer → {frame}")

    st.write("---")
    st.write("**Network Path**")
    for i, r in enumerate(["Sender"] + routers + ["Receiver"]):
        st.write(f"Packet at: {r}")
        st.graphviz_chart(network_diagram(packet_stage=f"Stage {i+1}"))
        time.sleep(delay)
        # Simulate packet loss at routers
        if loss > 0 and i != 0 and i != len(routers)+1:
            if random.randint(0,100) < loss:
                st.warning(f"Packet lost at {r}! Simulation stopped.")
                return

    st.write("---")
    st.write("**Decapsulation at Receiver**")
    try:
        step1 = frame.replace("ETH_FRAME[", "").rstrip("]")
        step2 = step1.split("[",1)[1].rstrip("]") if "[" in step1 else step1
        step3 = step2.split("[",1)[1].rstrip("]") if "[" in step2 else step2
        st.success("Application Received Message: " + step3)
    except Exception as e:
        st.error("Error during decapsulation: " + str(e))


# ----------------------------
# Main Execution
# ----------------------------
if simulate and message:
    if sim_type == "OSI Model Simulation":
        osi_model_simulator()
    else:
        tcp_ip_simulator()
else:
    st.info("Enter message and click Start Simulation")
