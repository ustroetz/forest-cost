## Forest Cost


### Overview

Forest Cost consist of two major modules: 
* [Cost Model](https://github.com/ustroetz/cost_model)
* [Log Road Model](https://github.com/ustroetz/log-road)
Additional information about the two can be found in their individual repositories. 

The Timber Harvest Cost Model estimates total delivered costs ($ US) from the stumpage to the mill gate for a timber stand.
The two main components of the model are the harvest cost ($ US/cubic foot) and the hauling cost ($ US/minute) which are estimated by the model. 
Harvest cost ($ US/cubic foot) is multipled by the total volume (cubic foot) of the stand. 
Hauling cost ($ US/minute) is multiplied by the total hauling time (minutes) from the landing to the mill gate and by the total necessary hauling trips. 
Both together result in the total delivered cost ($ US).
