import torch
import torchcontrol as toco

class KalmanFilter(toco.ControlModule):
    def __init__(self, 
                 X : torch.Tensor, 
                 dt : float = 0.001, 
                 x_cov : float = 1.0e-7, 
                 dx_cov : float = 0.0, 
                 obs_noise_cov : float = 1.2e-03):
        """Kalman Filter for linear dynamic system

        Args:
            X (torch.Tensor): initial state vector
            dt (float, optional): time step. Defaults to 0.001.
            x_cov (float, optional): convariance of poisition noise. Defaults to 1.0e-7.
            dx_cov (float, optional): covariance of velocity noise. Defaults to 0.0.
            obs_noise_cov (float, optional): covariance of observation noise. Defaults to 1.2e-03.
        """
        # Time interval
        self.size = torch.nn.Parameter(X.size(dim=0))

        # State vector
        self.X = torch.nn.Parameter(torch.cat((X,torch.zeros((self.size)))))

        # State vector
        self.X = torch.nn.Parameter(torch.cat((X, torch.zeros((self.sz,))), dim=0))

        # Motion Model
        self.F = torch.nn.Parameter(torch.diag(torch.ones(2 * self.sz)))
        self.F.data[:self.sz, self.sz:].copy_(torch.diag(torch.full((self.sz,), dt)))

        # Motion Noise Covariance
        self.Q = torch.nn.Parameter(torch.diag(torch.cat((torch.full((self.sz,), x_cov), torch.full((self.sz,), dx_cov)))))

        # Correlation Matrix
        self.P = self.Q

        # Observation Model
        self.H = torch.nn.Parameter(torch.zeros((7, 14)))
        self.H.data.copy_(torch.eye(7))

        # Observation Noise Covariance (load - grav)
        self.R = torch.nn.Parameter(torch.diag(torch.full((self.sz,), obs_noise_cov)))

        self.S = torch.nn.Parameter(torch.zeros((self.sz, self.sz)))
        self.K = self.X

    def forward(self, Z: torch.Tensor):
        self.X.data = torch.matmul(self.F, self.X)
        self.P.data = torch.matmul(torch.matmul(self.F, self.P), torch.transpose(self.F, 0, 1)) + self.Q

        self.S.data = torch.matmul(torch.matmul(self.H, self.P), torch.transpose(self.H, 0, 1)) + self.R
        self.K.data = torch.matmul(torch.matmul(self.P, torch.transpose(self.H, 0, 1)), torch.linalg.inv(self.S))
        self.X.data = self.X.data + torch.matmul(self.K, Z - torch.matmul(self.H, self.X))
        self.P.data = self.P.data - torch.matmul(torch.matmul(self.K, self.S), torch.transpose(self.K, 0, 1))
        return self.X.data[:self.sz]
