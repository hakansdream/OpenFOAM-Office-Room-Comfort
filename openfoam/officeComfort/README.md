# Office thermal comfort: OpenFOAM 14

A ready-to-run HVAC case for a two-person office on a summer design day.

It calculates the airflow and temperatures in the room, then evaluates thermal comfort to **EN ISO 7730**:

- **PMV:** predicted mean vote

- **PPD:** predicted percentage dissatisfied

- **DR:** draught rate

- **Age of air:** how long the air has been in the room

It uses the `fluid` solver module (`foamRun`) of OpenFOAM 14 (openfoam.org).

<br>

## The room

```
                      y = 4.0  corridor wall
     +--------------------------------------------------+
     |                                      [ return ]  |   ceiling:
     |   [light]                       [light]          |   - 4-way diffuser
     |                                                  |     in the centre
     |                  ___ jets ___                    |   - return grille
     |                 |  diffuser  |                   |     in the corner
     |                  ------------                    |   - 4 LED panels
     |      (person A)                 (person B)       |
     |   [====desk A====]          [====desk B====]     |
     |   [light]  [pc]                 [light] [pc]     |
     +--------[=========== window ===========]----------+
   x = 0                   y = 0  facade                x = 5.0
```

| Item | Size / position | Model |
|---|---|---|
| Room | 5.0 m x 4.0 m x 2.8 m high | facade with window at y = 0 |
| Window | 3.0 m x 1.4 m, sill at 0.9 m | U = 1.3 W/m²K, outdoor air 32 °C |
| External wall | rest of the facade | U = 0.35 W/m²K, outdoor air 32 °C |
| Internal walls, floor, ceiling | | adiabatic |
| Ceiling diffuser | 4-way, 600 x 600, room centre | 4 slots of 0.4 m x 0.05 m, jets 20° below the ceiling |
| Supply air | 300 m³/h at 18 °C | ≈ 5.4 air changes per hour |
| Return grille | 0.6 m x 0.3 m in the ceiling | pressure outlet |
| 2 occupants | 0.4 x 0.4 x 1.3 m boxes | 75 W sensible each |
| 2 computers + monitors | 0.6 x 0.2 x 0.36 m boxes on the desks | 100 W each |
| Lighting | 4 LED panels 0.6 x 0.6 m | 140 W in total |
| 2 desks | 1.6 m x 0.8 m, top at 0.74 m | adiabatic |

The total sensible heat gain is about 0.6 kW. Comfort is evaluated for summer clothing (0.5 clo), sedentary office work (1.2 met) and 50 % relative humidity.

<br>

## Running the case

Load OpenFOAM 14, then:

```bash
cp -r officeComfort $FOAM_RUN/
cd $FOAM_RUN/officeComfort
./Allrun
```

`Allrun` does the following:

1. Builds the mesh: `blockMesh` → `snappyHexMesh` (cuts out the desks, computers and people) → `createPatch` (cuts the diffuser slots, return grille, lights and window out of the walls).

2. Solves the steady flow on 4 cores for 3000 iterations: `decomposePar` → `foamRun` → `reconstructPar`. The last 5 solutions (iterations 2600 to 3000) are kept.

3. Sets the mean radiant temperature to the area-averaged surface temperature of the room envelope over the last 500 iterations.

4. Runs the comfort post-processing in `system/comfortFunctions.orig` on the last 5 solutions. This produces the PMV, PPD, DR and age fields.

5. Prints a summary with `./comfortReport`.

The mesh has about 164 000 cells. The whole run takes about 10 minutes on 4 cores.

Use `./Allclean` to remove all results.

To run on a different number of cores, change `numberOfSubdomains` and `n` in `system/decomposeParDict`.

<br>

## Results

`./comfortReport` prints this summary. All values are averaged over the last 500 iterations; min and max are over the last 5 solutions.

```
Air balance
    Supply air             300.1 m3/h at  18.0 degC
    Return air             305.4 m3/h at  23.2 degC

Heat balance
    Removed by the air       537 W   (m cp (T_return - T_supply))
    Heat gains               555 W   (people, computers, lights, facade)

Room temperatures
    Mean air                23.1 degC
    Mean radiant            24.5 degC

Occupied zone             mean      min      max
    T [degC]               23.0     21.4     30.1
    PMV [-]               -0.44    -1.02     0.82
    PPD [%]                 9.5      5.0     26.9
    DR [%]                  6.7      0.0     17.4
    Age of air [min]       11.0      9.8     11.8
```

<br>

What this means for this office:

- **On average the room meets category B,** but only just: PMV −0.44 (limit ±0.5) and PPD 9.5 % (limit 10 %). The room is on the slightly cool side.

- **Draught is acceptable:** mean DR is 6.7 % and the highest value is 17 %, below the 20 % limit. The highest draught is next to person A, where the jet towards the left wall comes down over desk A.

- **The coolest spots** (PMV down to −1.0) are at ankle height behind person A, where cool supply air collects on the floor, and in front of person A at desk height.

- **Mixing is good:** the mean age of air (11 min) is close to the nominal value V/Q = 55 m³ / 300 m³/h = 11 min.

- **The heat balance closes within about 3 %.** Expect a few percent here because the steady solution keeps oscillating slightly (see Sanity checks).

To make the room more neutral, try a supply temperature of 19–20 °C. You can also reduce the slot velocities on the person A side to cut the draught there.

<br>

Open the case in ParaView (`paraFoam`, or `touch office.foam` and open that file). Then look at:

- **Slices at z = 0.1 m, 0.6 m and 1.1 m:** ankle, waist and neck height of a seated person. These are the measurement heights of EN ISO 7726.

- **A vertical slice through the diffuser** (x = 2.5 m or y = 2.0 m): shows how the jets attach to the ceiling and where they drop.

- **Fields:** `T`, `U`, `PMV`, `PPD`, `DR`, `age`.

Monitored values are written to `postProcessing/` while the solver runs: residuals, supply and return flow, return air temperature, mean room temperature, probes behind each person, and wall heat flows.

<br>

### Comfort categories (EN ISO 7730)

| Category | PPD | PMV | DR |
|---|---|---|---|
| A | < 6 % | −0.2 < PMV < +0.2 | < 10 % |
| B | < 10 % | −0.5 < PMV < +0.5 | < 20 % |
| C | < 15 % | −0.7 < PMV < +0.7 | < 30 % |

Most offices are designed for category B.

Note that DR is only meaningful in the occupied zone. Right below the diffuser and along the ceiling, high DR values are expected.

<br>

### Sanity checks

- **Air balance:** the supply and return mass flow rates should be equal (`postProcessing/supplyFlowRate`, `postProcessing/returnFlowRate`).

- **Heat balance:** ṁ · cp · (T_return − T_supply) should equal the sum of the heat gains. The heat flow through each wall patch is in `postProcessing/wallHeatFlux/0/wallHeatFlux.dat`.

- **Convergence:** besides the residuals, check that the probe temperatures and `Tmean` have stopped changing. In this case the residuals level off at about 1e-2 and the probe temperatures keep oscillating by about ±0.3 K, while `Tmean` varies by less than 0.1 K. This is typical for buoyant room flows. It is why the report averages over the last 500 iterations.

- **Mesh:** for a real project, repeat the run on a finer mesh, for example one extra refinement level in `system/snappyHexMeshDict`, and compare the results.

<br>

## Changing the case

| What | Where |
|---|---|
| Supply air temperature, outdoor temperature | `Tsupply`, `Toutside` at the top of `0/T` |
| Supply air flow rate | scale the slot velocities in `0/U` (the comment there shows the calculation) |
| Heat gains of people, computers, lights | `Q` entries in `0/T` |
| Wall and window insulation | `h` entries in `0/T`, h = 1/(1/U − 0.13) |
| Clothing, activity, humidity | `system/comfortFunctions.orig` |
| Positions of furniture and people | `geometry` in `system/snappyHexMeshDict` |
| Positions of diffuser, return grille, lights, window | `system/createPatchDict` |
| Occupied zone used for the averages | `cellZone` boxes in `system/comfortFunctions.orig` |

<br>

**Winter case:** set `Toutside` to the winter design temperature (for example −3 °C), clothing to 1.0 clo, and use the supply temperature and flow of your heating design. Warm air from the ceiling tends to stay at the top of the room, so check the vertical temperature difference between 0.1 m and 1.1 m. EN ISO 7730 category B allows less than 3 K.

**Real geometry:** export furniture and people from CAD as STL or OBJ into `constant/geometry`, then use them in `system/snappyHexMeshDict` in place of the boxes. Keep the patch names, or update the names in `0/*`.

**Solar gain:** this case leaves out sunlight through the window. The simplest way to add it is a heat flux on the sunlit part of the floor: cut a patch out of the floor with `createPatchDict`, then give it `type externalTemperature; Q constant <W>;` in `0/T`. For a full treatment, add a radiation model (`fvDOM`), which also gives a proper mean radiant temperature.

<br>

## Modelling notes and limits

- **Steady RANS** (k-ω SST) with the Boussinesq approximation. The solver settings are those of the OpenFOAM `roomHeating` tutorial; the momentum predictor is switched off because it makes this case diverge. For final design numbers, you can continue the steady solution as a transient run (`ddtSchemes` `Euler`, as `roomHeating` does) and average over time.

- **No radiation model.** All sensible heat from people, computers and lights goes into the air by convection from their surfaces. As a result, these surfaces get hotter than in reality.

- **Mean radiant temperature** is one value for the whole room: the area-averaged temperature of the walls, floor, ceiling, window and lights. Local radiant asymmetry near the window is not captured.

- **The diffuser** is modelled with four slots that give the correct flow rate, discharge direction and jet momentum (the "momentum method"). For accurate results near the diffuser, use the effective area and throw from the manufacturer's data.

- **Humidity** is a constant input to the comfort calculation and is not solved for.
