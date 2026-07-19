# 🔌 How to Connect a Real PLC to Your Dashboard

Right now, your project uses `dummy_real_plc.py` to simulate live data. Because of the modular architecture I built, connecting your **actual PLC** is incredibly easy! All you have to do is create a new Python file that talks to the PLC, and then tell `main_real.py` to use that file instead of the dummy simulator.

Here is the step-by-step guide on how to do it.

---

## Step 1: Identify Your PLC Protocol
Different PLCs speak different languages. You need to know which protocol your sand plant PLC uses to communicate over the network. The most common ones are:
1. **Modbus TCP** (Very common for industrial equipment)
2. **OPC UA** (Modern, standard industrial protocol)
3. **Ethernet/IP** (Common on Allen-Bradley/Rockwell PLCs)
4. **S7 Communication** (Common on Siemens PLCs)

*Depending on the protocol, you will install a specific Python library.*

---

## Step 2: Install the Python Library
Open your VS Code terminal and install the library that matches your PLC:

* **For Modbus TCP:** `pip install pymodbus`
* **For OPC UA:** `pip install asyncua`
* **For Allen-Bradley (Ethernet/IP):** `pip install pylogix`
* **For Siemens S7:** `pip install python-snap7`

---

## Step 3: Create `real_plc.py`
Create a new file in your project folder called `real_plc.py`. This file will implement the exact same interface (`DataSource`) that the dummy PLC used, so the rest of the code doesn't need to change!

Here is an example of what `real_plc.py` looks like if your PLC uses **Modbus TCP**:

```python
import logging
from datetime import datetime, timezone
from pymodbus.client import ModbusTcpClient
from dummy_plc import DataSource

logger = logging.getLogger(__name__)

class RealSandPlantPLC(DataSource):
    def __init__(self, ip_address="192.168.1.100", port=502):
        self.client = ModbusTcpClient(ip_address, port=port)
        self.client.connect()
        logger.info(f"Connected to PLC at {ip_address}:{port}")

    def read_all(self):
        try:
            # Read holding registers from the PLC (e.g., address 0, count 22)
            # You will need to check your PLC memory map for the exact addresses!
            response = self.client.read_holding_registers(address=0, count=22, slave=1)
            
            if response.isError():
                logger.error("Failed to read from PLC")
                return []

            registers = response.registers
            
            # Map the raw registers to your column names
            record = {
                "Timestamp": datetime.now(tz=timezone.utc).isoformat(),
                "CYCLE_NO": registers[0],
                "COMP_PRESET_PCT": registers[1],
                "SAND_TEMP": registers[2],
                # ... map all 22 columns here ...
                "FINAL_MEASURE": registers[20],
                "Sand_Too_Wet_Fault": registers[21],
            }
            
            return [record]
            
        except Exception as e:
            logger.error(f"Error reading PLC: {e}")
            return []
            
    def close(self):
        self.client.close()
```

---

## Step 4: Map Your PLC Memory Addresses
In the code above, the PLC returns a list of raw numbers (`registers`). **This is the most important step:** You need to look at your PLC documentation or PLC programming software (like TIA Portal, RSLogix, etc.) to find the **Memory Map**. 

You must match the raw memory address from the PLC to the correct column name in your Python dictionary (e.g. knowing that Register 2 is the Sand Temperature).

---

## Step 5: Update `main_real.py` to use the Real PLC
Once your `real_plc.py` is reading data successfully, you just swap it out in your main script!

Open `main_real.py` and make these two small changes:

**1. Change the import at the top of the file:**
```python
# REMOVE THIS LINE:
# from dummy_real_plc import DummyRealPLC

# ADD THIS LINE:
from real_plc import RealSandPlantPLC
```

**2. Change the monitor initialization (around line 43):**
```python
class RealMonitor:
    def __init__(self) -> None:
        
        # REMOVE THIS LINE:
        # self._plc = DummyRealPLC()
        
        # ADD THIS LINE (Use your PLC's actual IP address!):
        self._plc = RealSandPlantPLC(ip_address="192.168.1.100")
        
        # ... the rest stays exactly the same ...
```

## That's It!
Run `python main_real.py` in your VS Code terminal just like before. 

Because we built the pipeline properly, the real PLC data will now flow straight into your CSV files, up to InfluxDB Cloud, and appear live on your Grafana dashboard!
