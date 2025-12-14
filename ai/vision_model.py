import torch
import torch.nn as nn
import numpy as np
from PIL import Image

class BotVisionCNN(nn.Module):
    def __init__(self, num_actions=5):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3, 32, 8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, 4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, stride=1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(3136, 512),
            nn.ReLU(),
            nn.Linear(512, num_actions)
        )
    
    def forward(self, x):
        return self.conv(x)

# Initialize model
model = BotVisionCNN()
model.load_state_dict(torch.load('vision_model.pth'))  # Load pre-trained
model.eval()

def process_vision(image_array):
    """
    image_array: 84x84x3 numpy array from bot's perspective
    returns: action probabilities
    """
    tensor = torch.from_numpy(image_array).permute(2, 0, 1).unsqueeze(0).float() / 255.0
    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1)
    return probs.numpy()[0]