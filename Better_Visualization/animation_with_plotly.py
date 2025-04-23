import plotly.graph_objects as go
import numpy as np
import os

# --- Your Data Loading ---
data_files = [
    (
        "Br1_trans",
        os.path.join(base_path, "Br1_trans/2s/Br1_trans_optd_gs_orb_1_XCD.log.CDV.dat"),
    ),
    (
        "Br2_trans",
        os.path.join(base_path, "Br2_trans/2s/Br2_trans_optd_gs_orb_1_XCD.log.CDV.dat"),
    ),
    (
        "Br3_trans",
        os.path.join(base_path, "Br3_trans/2s/Br3_trans_optd_gs_orb_1_XCD.log.CDV.dat"),
    ),
    (
        "Br4_trans",
        os.path.join(base_path, "Br4_trans/2s/Br4_trans_optd_gs_orb_1_XCD.log.CDV.dat"),
    ),
]

all_data = []
names = []
for name, file_path in data_files:
    try:
        data = np.loadtxt(file_path)
        all_data.append(data)
        names.append(name)
    except Exception as e:
        print(f"Warning: Could not load {file_path}. Error: {e}")

if not all_data:
    raise ValueError("No data loaded. Cannot create plot.")
# --- End Data Loading ---


# --- Create Figure and Add All Traces (Initially mostly hidden) ---
fig = go.Figure()

# Add each trace to the figure, making only the first one visible initially
for i, data in enumerate(all_data):
    fig.add_trace(
        go.Scatter(
            x=data[:, 0],
            y=data[:, 1],
            mode="lines",
            name=names[i],
            visible=(i == 0),  # Only the first trace (i=0) is visible at the start
        )
    )

# --- Add Shapes and Layout (Apply to the base figure) ---
# Add horizontal lines at 0.001 and -0.001
fig.add_shape(
    type="line",
    x0=1750,
    x1=1770,
    y0=0.001,
    y1=0.001,
    line=dict(color="black", width=1, dash="dash"),
)
fig.add_shape(
    type="line",
    x0=1750,
    x1=1770,
    y0=-0.001,
    y1=-0.001,
    line=dict(color="black", width=1, dash="dash"),
)

# Update layout
fig.update_layout(
    xaxis_title="Energy [eV]",
    yaxis_title="Intensity [a.u.]",
    xaxis=dict(range=[1750.0, 1770.0]),
    legend_title_text="",
    title="Sequential Plot Animation",  # Optional: Add a title
)

# --- Create Animation Frames ---
frames = []
for k in range(1, len(all_data)):  # Start from the second trace (index 1)
    frame = go.Frame(
        data=[
            # This dictionary targets the k-th trace (0-indexed)
            # and sets its 'visible' property to True for this frame.
            # Traces before k remain visible from previous frames.
            {"visible": True}
        ],
        name=names[k],  # Name the frame after the trace being added
        traces=[k],  # Specify which trace index this frame's data dict refers to
    )
    frames.append(frame)

# Assign frames to the figure
fig.frames = frames


# --- Configure Animation Controls (Play Button and Slider) ---
def frame_args(duration):
    return {
        "frame": {"duration": duration, "redraw": True},  # Redraw is important
        "mode": "immediate",
        "fromcurrent": True,
        "transition": {"duration": duration, "easing": "linear"},
    }


fig.update_layout(
    updatemenus=[
        {
            "buttons": [
                {
                    "args": [None, frame_args(500)],  # None uses the defined frames
                    "label": "&#9654;",  # Play symbol
                    "method": "animate",
                },
                {
                    "args": [[None], frame_args(0)],  # Pause animation
                    "label": "&#9724;",  # Pause symbol
                    "method": "animate",
                },
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 70},  # Adjust padding
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top",
        }
    ],
    sliders=[
        {
            "active": 0,  # Start slider at the beginning (base state)
            "yanchor": "top",
            "xanchor": "left",
            "currentvalue": {
                "font": {"size": 16},
                "prefix": "Showing: ",
                "visible": True,
                "xanchor": "right",
            },
            "transition": {"duration": 300, "easing": "cubic-in-out"},
            "pad": {"b": 10, "t": 50},  # Adjust padding
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": [
                # Step for the initial state (only first trace visible)
                {
                    "args": [
                        [f.name for f in fig.frames],
                        frame_args(0),
                    ],  # Go to base state requires resetting visibility potentially
                    # We need a way to revert to the base state explicitly if slider moves back.
                    # Let's redefine args to set visibility explicitly for step 0
                    "label": names[0],
                    "method": "animate",
                    "args": [
                        # Frame name target is tricky for base state, let's set visibility directly
                        # Create a list of visibility states for the base step
                        [{"visible": (i == 0)} for i in range(len(all_data))],
                        {
                            "mode": "immediate",
                            "transition": {"duration": 0},
                            # No 'frame' dict here as we're not animating to a named frame
                        },
                    ],
                    "method": "restyle",  # Use restyle for direct property setting
                }
            ]
            +
            # Steps for each subsequent frame
            [
                {
                    "args": [[f.name], frame_args(300)],
                    "label": f.name,
                    "method": "animate",
                }
                for f in fig.frames  # Create a step for each defined frame
            ],
        }
    ],
)


# --- Show the Figure ---
fig.show()
