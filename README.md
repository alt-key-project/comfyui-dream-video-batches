# Dream Project Video Batches

This is a custom node pack for ComfyUI, intended to provide utilities for other custom node sets for AnimateDiff and Stable Video Diffusion workflows. 

I produce these nodes for my own video production needs (as "Alt Key Project" - [Youtube channel](https://www.youtube.com/channel/UC4cKvJ4hia7zULxeCc-7OcQ)). However, I think the nodes may be useful for other people as well.

I also run a separate [Youtube channel](https://www.youtube.com/channel/UCguzih0_nXb6eSFLNWE7pmQ) for "Dream Project", 
where any videos related to my AI art generation will appear, including tutorials for my node packs (this one and the older "Dream Project Animation Nodes"). Currently, there are no videos for for "Dream Project Video Batches" but that is only a question of time.

## Installation

### Simple option (soon)

You should soon be able to install Dream Project Video Batches node pack using the ComfyUI Manager.

### Manual option

Run within (ComfyUI)/custom_nodes/ folder:

* git clone https://github.com/alt-key-project/comfyui-dream-video-batches.git
* cd comfyui-dream-video-batches

Then, if you are using the python embedded in ComfyUI:
* (ComfyUI)/python_embedded/python.exe -s -m pip install -r requirements.txt

With your system-wide python:
*  pip install -r requirements.txt

Finally:
* Start ComfyUI.

### Also install

As mentioned, this node pack is intended to support other node packs. A few worth mentioning are:

* ComfyUI Frame Interpolation (by Fannovel16)
* AnimateDiff Evolved (by Kosinkadink)
* ComfyUI-VideoHelperSuite (by Kosinkadink)
* ComfyUI Stable Video Diffusion (by thecooltechguy)

## Concepts

### Frame Set

A Frame set is a number of images (in a batch), with frame indices and a frame rate. Most nodes in this node pack work 
with frame sets.

### Camera

The camera nodes in the node pack are always animating cropping tools - the output should always be smaller in size than 
the input (to allow for camera "movement").

## The Nodes

### Blended Transition [DVB]
Fades from one frame set to another over a specified number of overlapping frames.

### Calculation [DVB]
Maths node providing arithmetic operators and most common mathematical functions (as defined in Python math module).

### Create Frame Set [DVB]
Creates a frame set from an image batch and a specified frame rate.

### Divide [DVB]
Simple division of float or int.

### Fade From Black [DVB]
Adds fade-in from black at beginning of frame set.
 
### Fade To Black [DVB]
Adds fade-out to black at end of frame set.

### Float Input [DVB]
User input node for float values.

### For Each Done [DVB]
File iteration (finalizer for use with 'For Each Filename')". This is used to process all files in a directory matching 
a pattern. This node marks a filename as "processed" and should typically be added very late in the workflow.

### For Each Filename [DVB]
File iteration. This is used to process all files in a directory matching 
a pattern. This provides the next file path to process.

### Frame Set Append [DVB]
Appends a frame set to another.

### Frame Set Frame Dimensions Scaled [DVB]
Recalculates frame dimensions of a frame set with a factor. Useful to calculate intermediate step sizes.

### Frame Set Index Offset [DVB]
Offsets frame indices in frame set.

### Frame Set Merger [DVB]
Merges two frame sets. Conflicting indices will be prioritized from either set based on the arguments.

### Frame Set Reindex [DVB]
Reindexing of frames in frame set (replacing all existing indices).

### Frame Set Repeat [DVB]
Repeats a frame set multiple times. Useful for instance to quickly create alonger animation from a loop or single image.

### Frame Set Reverse [DVB]
Reverses the frames of an animation (index flip). The flip is done in index order but will otherwise disregard indexing 
(such as gaps).

### Frame Set Split Beginning [DVB]
Splits a frame set into a part of specified length (in existing frames) at the beginning and the following frames.

### Frame Set Split End [DVB]
Splits a frame set into a part of specified length (in existing frames) at the end and the previous frames.

### Frame Set Splitter [DVB]
Splits a frame set into two evenly sized sets (based on number of existing frames). Useful to divide work 
(reduce memory requirements in some cases).

### Generate Inbetween Frames [DVB]
Simple utility for quickly adding inbetween frames (filling gaps) in frame set.

### Int Input [DVB]
User input node for float values.

### Linear Camera Pan [DVB]
Cropping utility to perform a camera constant velocity pan within a frame set. Outputs a frame set of smaller frame size.

### Linear Camera Roll [DVB]
Rolls the camera along z axis. 

### Linear Camera Zoom [DVB]
Linear (constant velocity) zoom through crop.

### Load Image From Path [DVB]
Loads a single image file from a path.

### Multiply [DVB]
Simple multiplication node.

### Sine Camera Pan [DVB]
Cropping utility to perform a camera pan within a frame set. Outputs a frame set of smaller frame size. Sine oscillation.

### Sine Camera Roll [DVB]
Rolls the camera along z axis - sine oscillation.

### Sine Camera Zoom [DVB]
Oscillating (sine wave) zoom through crop.

### String Input [DVB]
User input node for string values.

### Text Input [DVB]
User input node for text(string) values.

### Unwrap Frame Set [DVB]
Extracts contents of frame set (required for use with other custom node packs and/or output nodes).
