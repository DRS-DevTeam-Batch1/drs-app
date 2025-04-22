
# Pre-Processing

## Input Data Format

- **x**: horizontal position  
- **y**: lengthwise position (toward batsman)  
- **z**: height (vertical)  
- **t**: spin value (scalar)

The input data file consists of the axis of the ball along with its spin in the format given below:

```json
[
    {"x": 2.4, "y": 1.2, "z": 0.6, "t": 0.1},
    {"x": 2.2, "y": 1.0, "z": 0.4, "t": 0.1}
]
```

# Removing Missing Values

To pre-process the data before doing trajectory analysis, we must first identify and remove missing or ambiguous data rows.

Steps:
1. Load the data using the pandas library.
2. Create a DataFrame.
3. Remove missing (`NaN`) entries.

```python
df = pd.DataFrame(data)
df.dropna(inplace=True)
```

# Normalization

Next, we normalize the data to a [0, 1] scale using `MinMaxScaler`.  
This rescaling ensures values fall within the 0 to 1 range using min-max normalization, with the help of the `sklearn` library:

```python
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
df[['x', 'y', 'z']] = scaler.fit_transform(df[['x', 'y', 'z']])
```

# Pre-Processed

Now the data has been pre-processed:
- All missing or ambiguous values have been eliminated.
- Values are normalized to the range [0, 1] for further use.

---

We can now calculate the velocity of the ball using these `x`, `y`, `z`, and `t` values, which will correctly predict the trajectory for the dataset.
