import streamlit as st
from graphviz import Digraph

st.set_page_config(page_title="Advanced TCP/IP Simulator", layout="wide")

st.title("🌐 Advanced TCP/IP Model Simulator")
st.write("Simulate packet flow from Sender → Router → Receiver")

# Sidebar Inputs
st.sidebar.header("Simulation Settings")
protocol = st.sidebar.selectbox("Transport Protocol", ["TCP", "UDP"])
message = st.sidebar.text_input("Enter Message")
src_ip = st.sidebar.text_input("Source IP", "192.168.1.10")
dst_ip = st.sidebar.text_input("Destination IP", "192.168.1.20")
src_port = st.sidebar.text_input("Source Port", "5000")
dst_port = st.sidebar.text_input("Destination Port", "80")
simulate = st.sidebar.button("Start Simulation")


def encapsulate(data):
    app = data
    if protocol == "TCP":
        transport = f"TCP(src_port={src_port}, dst_port={dst_port})[{app}]"
    else:
        transport = f"UDP(src_port={src_port}, dst_port={dst_port})[{app}]"
    internet = f"IP(src={src_ip}, dst={dst_ip})[{transport}]"
    frame = f"ETH_FRAME[{internet}]"
    return app, transport, internet, frame


def network_diagram():
    g = Digraph()
    g.node("A", "Sender")
    g.node("B", "Router")
    g.node("C", "Receiver")
    g.edge("A", "B", label="Packet")
    g.edge("B", "C", label="Forward")
    return g


if simulate and message != "":
    st.subheader("1️⃣ Encapsulation Process")
    app, transport, internet, frame = encapsulate(message)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("Application Layer")
        st.write(app)
    with col2:
        st.warning("Transport Layer")
        st.write(transport)
    with col3:
        st.success("Internet Layer")
        st.write(internet)
    with col4:
        st.error("Network Access Layer")
        st.write(frame)

    st.divider()
    st.subheader("2️⃣ Network Path")
    st.graphviz_chart(network_diagram())

    st.divider()
    st.subheader("3️⃣ Packet Sent Over Network")
    st.code(frame)

    st.divider()
    st.subheader("4️⃣ Router Processing")
    st.write("Router reads destination IP:", dst_ip)
    st.write("Router forwards packet to receiver")

    st.divider()
    st.subheader("5️⃣ Decapsulation at Receiver")

    # Safe Decapsulation
    try:
        # Remove Ethernet Header
        step1 = frame.replace("ETH_FRAME[", "").rstrip("]")
        st.write("Remove Ethernet Header:", step1)

        # Remove IP Header
        if "[" in step1:
            step2 = step1.split("[", 1)[1].rstrip("]")
        else:
            step2 = step1
        st.write("Remove IP Header:", step2)

        # Remove Transport Header
        if "[" in step2:
            step3 = step2.split("[", 1)[1].rstrip("]")
        else:
            step3 = step2
        st.write("Remove Transport Header:", step3)

        # Final Application Data
        st.success("Application Received Message: " + step3)

    except Exception as e:
        st.error("Error during decapsulation: " + str(e))

else:
    st.info("Enter parameters and click Start Simulation")
