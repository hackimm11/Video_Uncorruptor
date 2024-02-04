# Video uncorruptor
## Overview
This program manage to find the original video of a corrupted one, where the frames are shuffled, and there is also some wrong frames.

So it works on two main steps with different approaches, the first is to clean the video from wrong frames using histograms as characteristic, and find the least correlated frames to the median histogram using IQR based thresholed.
The second step is to put these clean frames in the right order, using euclidean distance based approach, where a frames are close to each other with a minimal distance.
finally we put the two main steps together to write the video, in two final orders (we can't know the right direction with a code, which is practically he only limitation)

## Usage
Execute the main file in src file folder directly, where there is also the uncorruptor class. The corrupted video must be in the input folder, the final videos given by the code weill be written in the output folder.
You can check a version of my personal results in the results file.




