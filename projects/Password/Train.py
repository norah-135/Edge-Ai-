import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "my_keystrokes.csv")
OUTPUT_HEADER_PATH = os.path.join(BASE_DIR, "model.h")


X = np.genfromtxt(CSV_PATH, delimiter=',')
if X.ndim == 1:
    X = np.expand_dims(X, axis=0)
X = X[:, :15]

mins = np.min(X, axis=0)
maxs = np.max(X, axis=0)

tolerance = 0.35
lower_bounds = mins * (1.0 - tolerance)
upper_bounds = maxs * (1.0 + tolerance)

header_content = f"""#pragma once

class KeystrokeBaseline {{
public:
    const float lower_bounds[15] = {{
        {", ".join([f"{val:.6f}f" for val in lower_bounds])}
    }};

    const float upper_bounds[15] = {{
        {", ".join([f"{val:.6f}f" for val in upper_bounds])}
    }};

    int predict(float *x) {{
        for (int i = 0; i < 15; i++) {{
            if (x[i] < lower_bounds[i] || x[i] > upper_bounds[i]) {{
                return 0; 
            }}
        }}
        return 1; 
    }}
}};
"""

with open(OUTPUT_HEADER_PATH, 'w') as f:
    f.write(header_content)

print("=" * 60)
print("[SUCCESS] New precise bounding model generated!")
print("=" * 60)