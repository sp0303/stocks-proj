import torch
import torch.nn as nn

class StockTransformer(nn.Module):
    def __init__(self, feature_size, num_heads, num_layers, seq_length=60, dropout=0.2):
        super().__init__()
        
        # Positional Encoding (Learned embedding for fixed sequence length)
        self.pos_embedding = nn.Parameter(torch.zeros(1, seq_length, feature_size))
        self.dropout = nn.Dropout(dropout)

        self.encoder_layer = nn.TransformerEncoderLayer(
            d_model=feature_size,
            nhead=num_heads,
            batch_first=True,
            dropout=dropout
        )

        self.transformer = nn.TransformerEncoder(
            self.encoder_layer,
            num_layers=num_layers
        )

        self.fc = nn.Linear(feature_size, 1)

    def forward(self, x):
        # x shape: (batch, seq_len, feature_size)
        x = x + self.pos_embedding
        x = self.dropout(x)
        
        x = self.transformer(x)
        x = x[:, -1, :]  # last time step
        out = self.fc(x)
        return out
