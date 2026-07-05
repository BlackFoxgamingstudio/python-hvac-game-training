# RPG System Blueprint: Electrical Grid & DDC Control Loops

Defines the voltage nodes, wiring loops, current meters, and automated DDC logic rules.

## 🗺️ System Topology

```mermaid
flowchart TD
    PowerSource["208V AC Line Source"] --> MainBreaker["Main Overcurrent Breaker"]
    MainBreaker --> Contactor["Compressor Magnetic Contactor"]
    MainBreaker --> FanRelay["Evaporator Fan Speed Relay"]
    
    Contactor --> CompMotor["Compressor Motor Stator"]
    FanRelay --> FanMotor["Evaporator Fan Motor windings"]
    
    MicroController["DDC Controller Node"] -- "24V Control Signal" --> Contactor
    MicroController -- "24V Control Signal" --> FanRelay
    
    classDef power fill:#2a1f10,stroke:#d4ac0d,stroke-width:2px,color:#fff;
    classDef control fill:#0d1b2a,stroke:#1b4965,stroke-width:2px,color:#fff;
    class PowerSource,MainBreaker,Contactor,FanRelay,CompMotor,FanMotor power;
    class MicroController control;
```

## 💡 DDC Logic Specifications

### Thermostat Deadband Checks
```python
if current_temp > setpoint + deadband:
    stage_cooling_on()
elif current_temp < setpoint - deadband:
    stage_cooling_off()
```
