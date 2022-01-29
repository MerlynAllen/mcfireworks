from PIL import Image
import numpy as np

img = Image.open("Untitled.bmp").convert("L")
img = np.where(np.array(img) > 0, "0", "1").tolist()
print("\n".join(["".join(row) for row in img]))