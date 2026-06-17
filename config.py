
class Config:

    # Networking
    onlineMode = True
    #server = "ws://178.63.171.186:2027"
    server = "ws://127.0.0.1:2026"

    # Runtime
    campaign = None
    net = None
    worldViewport = None

    # Grid config
    gridSize = 10
    gridColor = (170, 170, 170, 40)
    gridThickness = 2

    # Z Layers
    zBackground = -50
    zGrid = -49
    zUnits = 1
    zFOW = 10

    # Vector2 settings
    maxError = 0.1
    unitLerpFreq = 60
    unitLerpFactor = 0.08
