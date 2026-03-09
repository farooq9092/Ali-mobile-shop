import streamlit as st
import pandas as pd
import random
import time
import networkx as nx
import matplotlib.pyplot as plt

# ===============================
# DHCP SERVER CLASS
# ===============================

class DHCPServer:

    def __init__(self, name, network, start, end, lease_time):

        self.name = name
        self.network = network
        self.start = start
        self.end = end
        self.lease_time = lease_time

        self.available_ips = [network + str(i) for i in range(start, end + 1)]
        self.leases = {}
        self.offers = {}

    def discover(self, mac):

        if mac in self.leases:
            return self.leases[mac]["ip"]

        if len(self.available_ips) == 0:
            return None

        ip = random.choice(self.available_ips)
        self.offers[mac] = ip

        return ip

    def request(self, mac):

        if mac not in self.offers:
            return None

        ip = self.offers[mac]

        if ip not in self.available_ips:
            return None

        self.available_ips.remove(ip)

        lease = {
            "ip": ip,
            "start": time.time(),
            "expiry": time.time() + self.lease_time
        }

        self.leases[mac] = lease
        del self.offers[mac]

        return ip

    def cleanup(self):

        expired = []

        for mac in self.leases:
            if time.time() > self.leases[mac]["expiry"]:
                expired.append(mac)

        for mac in expired:

            ip = self.leases[mac]["ip"]

            self.available_ips.append(ip)

            del self.leases[mac]

# ===============================
# CLIENT
# ===============================

class DHCPClient:

    def __init__(self):

        self.mac = self.generate_mac()
        self.ip = None

    def generate_mac(self):
        return "02:00:%02x:%02x:%02x:%02x" % tuple(
            random.randint(0,255) for _ in range(4)
        )

# ===============================
# SESSION STATE
# ===============================

if "servers" not in st.session_state:
    st.session_state.servers = []

if "clients" not in st.session_state:
    st.session_state.clients = []

if "logs" not in st.session_state:
    st.session_state.logs = []

# ===============================
# LOGGING
# ===============================

def log(msg):
    st.session_state.logs.append({
        "time": time.strftime("%H:%M:%S"),
        "event": msg
    })

# ===============================
# UI
# ===============================

st.set_page_config(page_title="Ultimate DHCP Lab", layout="wide")

st.title("🧪 Ultimate DHCP Network Lab")

# ===============================
# SIDEBAR CONFIG
# ===============================

st.sidebar.header("Add DHCP Server")

name = st.sidebar.text_input("Server Name", "DHCP-Server")
network = st.sidebar.text_input("Network Prefix", "192.168.1.")
start = st.sidebar.number_input("Start IP", 100)
end = st.sidebar.number_input("End IP", 120)
lease = st.sidebar.slider("Lease Time", 60, 600, 120)

if st.sidebar.button("Add Server"):

    server = DHCPServer(name, network, start, end, lease)
    st.session_state.servers.append(server)

    log(f"Server {name} added")

# ===============================
# CLIENT GENERATOR
# ===============================

st.sidebar.header("Clients")

if st.sidebar.button("Add Client"):

    client = DHCPClient()
    st.session_state.clients.append(client)

    log(f"Client {client.mac} joined network")

# ===============================
# ATTACK SIMULATIONS
# ===============================

st.sidebar.header("Attack Simulation")

if st.sidebar.button("DHCP Starvation Attack"):

    for i in range(30):

        client = DHCPClient()
        st.session_state.clients.append(client)

    log("DHCP starvation attack triggered")

if st.sidebar.button("Add Rogue DHCP Server"):

    rogue = DHCPServer("Rogue-DHCP", "10.0.0.", 50, 100, 300)
    st.session_state.servers.append(rogue)

    log("Rogue DHCP server deployed")

# ===============================
# DHCP PROCESS
# ===============================

if st.button("Run DHCP Cycle"):

    for client in st.session_state.clients:

        if client.ip is None:

            log(f"{client.mac} DISCOVER")

            for server in st.session_state.servers:

                offer = server.discover(client.mac)

                if offer:

                    log(f"{server.name} OFFER {offer}")

                    ip = server.request(client.mac)

                    if ip:
                        client.ip = ip
                        log(f"{client.mac} ACK {ip}")
                        break

# ===============================
# CLEANUP
# ===============================

for server in st.session_state.servers:
    server.cleanup()

# ===============================
# LEASE TABLE
# ===============================

st.subheader("Active DHCP Leases")

rows = []

for server in st.session_state.servers:

    for mac in server.leases:

        lease = server.leases[mac]

        rows.append({
            "Server": server.name,
            "MAC": mac,
            "IP": lease["ip"],
            "Expires": int(lease["expiry"] - time.time())
        })

df = pd.DataFrame(rows)

st.dataframe(df, use_container_width=True)

# ===============================
# POOL USAGE
# ===============================

st.subheader("IP Pool Usage")

for server in st.session_state.servers:

    total = server.end - server.start + 1
    used = len(server.leases)

    st.write(server.name)

    st.progress(used / total)

# ===============================
# NETWORK TOPOLOGY
# ===============================

st.subheader("Network Topology")

G = nx.Graph()

for server in st.session_state.servers:
    G.add_node(server.name, color="red")

for client in st.session_state.clients:
    G.add_node(client.mac, color="blue")

for client in st.session_state.clients:
    if client.ip:
        for server in st.session_state.servers:
            if client.mac in server.leases:
                G.add_edge(server.name, client.mac)

colors = [G.nodes[n].get("color","gray") for n in G.nodes]

fig, ax = plt.subplots()

nx.draw(G, with_labels=True, node_color=colors, ax=ax)

st.pyplot(fig)

# ===============================
# EVENT LOG
# ===============================

st.subheader("Packet Event Log")

log_df = pd.DataFrame(st.session_state.logs)

st.dataframe(log_df, use_container_width=True)
