# BT-SmartDry

AI monitoring and advisory system for IoT smart solar dryers operated by women-led hubs.

## Language

**Batch**:
A discrete load of a single crop placed into a dryer. Multiple batches of different crops can coexist in the same dryer simultaneously, each tracked independently.
_Avoid_: run, session, lot

**Hub**:
A women-led drying facility at a fixed geographic location (Meru, Tharaka Nithi, or Eldoret).
_Avoid_: site, station, plant

**Reading**:
A single set of sensor measurements captured at one point in time for one batch.
_Avoid_: data point, log entry, measurement

**Advisory**:
A plain-language message telling the operator what to do next, derived from ML predictions.
_Avoid_: recommendation, alert, notification

**Quality Grade**:
The predicted final classification of a dried batch: Export, Standard, or Downgraded.
_Avoid_: quality score, rating, tier

**Operator**:
A hub worker who loads batches, monitors drying, and acts on advisories.
_Avoid_: user, farmer, technician

**Administrator**:
The founder-operator role with visibility across all hubs.
_Avoid_: admin, superuser, manager

**Alert**:
An SMS sent to the operator's phone when a batch reaches a trigger condition (near-completion, completion, or anomaly).
_Avoid_: notification, push, message

**Dryer Capacity**:
The maximum total weight (kg) of crop a hub's dryer can hold at once. Currently 200 kg for all hubs.
_Avoid_: limit, maximum load

**Drying Cycle**:
The full process from loading a crop batch into a dryer to removing the dried product.
_Avoid_: run, session, process

**Over-drying**:
When dried crop remains in the dryer past its optimal moisture target, degrading quality grade.
_Avoid_: burning, spoiling

