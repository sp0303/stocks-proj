import torch
import torch.nn as nn


class StockTransformer(nn.Module):

    def __init__(self, feature_size, num_heads, num_layers):

        super().__init__()

        self.encoder_layer = nn.TransformerEncoderLayer(
            d_model=feature_size,
            nhead=num_heads,
            batch_first=True
        )

        self.transformer = nn.TransformerEncoder(
            self.encoder_layer,
            num_layers=num_layers
        )

        self.fc = nn.Linear(feature_size, 1)

    def forward(self, x):

        x = self.transformer(x)

        x = x[:, -1, :]  # last time step

        out = self.fc(x)

        return out
