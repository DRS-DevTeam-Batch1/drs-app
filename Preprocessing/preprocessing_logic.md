#Pre-Processing
##Input Data Format :
x: horizontal position
y: lengthwise position (toward batsman)
z: height (vertical)
t: spin value (scalar)
 
The input datafile consists of the axis of the ball along with its spin in the format given below:
[
   {"x": 2.4, "y": 1.2, "z": 0.6, "t": 0.1},
    {"x": 2.2, "y": 1.0, "z": 0.4, "t": 0.1},
]
 
##Remove Missing values:
As to pre-process the data before doing trajectory analysis on it we must first distinguish the missing, or ambiguous data rows by removing them.
For this purpose we first load the data using pandas library and make a dataframe.
Next we clean the data by removing missing (Nan) entries from it 
 
df = pd.DataFrame(data)
df.dropna(inplace=True)
 
##Normalization:
Next we normalize the data to a [0,1] scale using MinMaxScalar which makes it between 0 to 1 range using min-max normalzation by using sklearn library for pre-processing.


from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
df[['x', 'y', 'z']] = scaler.fit_transform(df[['x', 'y', 'z']])
 
##Pre-processed:
Now the data has been pre-processed and all the missing or ambiguous values  are eliminated and the values are normalized  in the range [0,1] for further use.
 
 
Now we may calculate the velocity of the ball and using these x,y,z and t values which will correctly predict the trajectory for the dataset.
