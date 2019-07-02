## AWS Stop/Start resources based on Tags for scheduling

The function will run on an hourly basis and stop or start AWS instances according to a schedule defined in `AUTO_START` or `AUTO_STOP` Tags.

Schedule Tag values consists of an hour with an optional timezone (the default is `UTC`) and optionally the week days to which the schedule applies.

**Every day**:

- `07 Europe/Paris` will stop or start an instance every days at 7AM in Paris timezone 
- `07` will will stop or start an instance every days at 7AM UTC

**Specific days of the week**

- `SUN,WED 08 America/Tonroto` will stop or start an instance at 7AM in Tonroto timezone only on Sundays and on Wednesdays
- `MON 08` will stop or start an instance every Mondays at 8AM UTC

**Days range**

- `MON-FRI 22 Europe/London` will stop or start an instance on work days at 22PM in London timezone
- `SAT-SUN 22` will stop or start an instance on weekends at 22PM UTC
