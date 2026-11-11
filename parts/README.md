# parts

One module per hardware component (camera, steering servo, throttle motor, controller, ...).

Part convention (as in Donkeycar):

- `run(*inputs)` returns the part's outputs (called every loop tick), or
- `update()` runs in its own thread, with `run_threaded(*inputs)` returning the latest outputs
- optional `shutdown()` releases hardware
