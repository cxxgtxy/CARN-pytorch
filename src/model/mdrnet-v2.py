import torch.nn as nn
import model.ops as ops

class Net(nn.Module):
    def __init__(self, scale):
        super(Net, self).__init__()
        self.relu = nn.ReLU()
        
        self.entry = nn.Conv2d(3, 64, 3, 1, 1, bias=False)
        self.blocks = nn.Sequential(
            # stem
            ops.BasicBlock(64, 64, dilation=1, act=self.relu),
            ops.BasicBlock(64, 96, dilation=1, act=self.relu),

            # MDR blocks
            *[ops.MDRBlockB(96, 32, 96, dilation=[2, 4], act=self.relu) for _ in range(8)],

            # exit   
            ops.BasicBlock(96, 64, dilation=1, act=self.relu),
        )
        self.upsample = ops.UpsampleBlock(64, scale)
        self.exit = nn.Sequential(
            nn.Conv2d(64, 3, 3, 1, 1)
        )

        self.sub_mean = ops.MeanShift((0.4488, 0.4371, 0.4040), sub=True)
        self.add_mean = ops.MeanShift((0.4488, 0.4371, 0.4040), sub=False)
        
    def forward(self, x):
        x = self.sub_mean(x)
        x = self.entry(x)
        
        out = self.blocks(x)
        out += x

        out = self.upsample(out)
        out = self.exit(out)
        
        out = self.add_mean(out)

        return out
