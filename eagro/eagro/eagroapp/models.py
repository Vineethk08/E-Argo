from django.db import models
from django.contrib.auth.models import AbstractUser

# PyTorch imports - optional, only needed for disease detection
try:
    import torch 
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    # Create dummy classes for when torch is not available
    class nn:
        class Module:
            pass
        class Sequential:
            pass
        class Conv2d:
            pass
        class BatchNorm2d:
            pass
        class MaxPool2d:
            pass
        class Linear:
            pass
        class ReLU:
            pass
    class F:
        pass

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_user = models.BooleanField(default=False)

    class Meta:
        swappable = 'AUTH_USER_MODEL'



def ConvBlock(in_channels, out_channels, pool=False):
    layers = [nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
             nn.BatchNorm2d(out_channels),
             nn.ReLU(inplace=True)]
    if pool:
        layers.append(nn.MaxPool2d(4))
    return nn.Sequential(*layers)


# Model Architecture
class ResNet9(nn.Module if TORCH_AVAILABLE else object):
    def __init__(self, in_channels, num_diseases):
        super().__init__()
        
        self.conv1 = ConvBlock(in_channels, 64)
        self.conv2 = ConvBlock(64, 128, pool=True) # out_dim : 128 x 64 x 64 
        self.res1 = nn.Sequential(ConvBlock(128, 128), ConvBlock(128, 128))
        
        self.conv3 = ConvBlock(128, 256, pool=True) # out_dim : 256 x 16 x 16
        self.conv4 = ConvBlock(256, 512, pool=True) # out_dim : 512 x 4 x 44
        self.res2 = nn.Sequential(ConvBlock(512, 512), ConvBlock(512, 512))
        
        self.classifier = nn.Sequential(nn.MaxPool2d(4),
                                       nn.Flatten(),
                                       nn.Linear(512, num_diseases))
        
    def forward(self, xb): # xb is the loaded batch
        out = self.conv1(xb)
        out = self.conv2(out)
        out = self.res1(out) + out
        out = self.conv3(out)
        out = self.conv4(out)
        out = self.res2(out) + out
        out = self.classifier(out)
        return out