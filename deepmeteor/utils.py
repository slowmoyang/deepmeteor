from dataclasses import asdict, dataclass
import numpy as np
import numpy.typing as npt
import vector
import matplotlib.pyplot as plt


class MissingET(vector.MomentumNumpy2D):

    @classmethod
    def from_array(cls, array, cylindrical):
        component_list = ['pt', 'phi'] if cylindrical else ['px', 'py']
        return cls({component: array[:, idx]
                    for idx, component in enumerate(component_list)})

    @classmethod
    def from_npy(cls, path, cylindrical):
        array = np.load(path)
        return cls.from_array(array, cylindrical)

    @classmethod
    def from_tensor(cls, tensor, cylindrical: bool = False):
        array = tensor.detach().cpu().numpy()
        return cls.from_array(array, cylindrical)

    @classmethod
    def from_tree(cls, tree, algo: str):
        data = tree.arrays([f'{algo}_pt', f'{algo}_phi'], library='np')
        data = {key.removeprefix(f'{algo}_'): value
                for key, value in data.items()}
        return cls(data)

    def __getitem__(self, key):
        return getattr(self, key)


def compute_residual(lhs: MissingET, rhs: MissingET, component: str):
    if component == 'phi':
        residual = lhs.deltaphi(rhs)
    else:
        residual = lhs[component] - rhs[component]
    return residual


@dataclass
class Errorbar:
    x: npt.NDArray[np.float32]
    y: npt.NDArray[np.float32]
    xerr: npt.NDArray[np.float32]
    yerr: npt.NDArray[np.float32]

    def to_npz(self, path):
        np.savez(path, **asdict(self))

    @classmethod
    def from_npz(cls, path):
        npz_file = np.load(path)
        kwargs = {key: npz_file[key] for key in npz_file.keys()}
        return cls(**kwargs)

    @property
    def xlow(self):
        return self.x[0] - self.xerr[0]

    @property
    def xup(self):
        return self.x[-1] + self.xerr[-1]

    def plot(self, ax=None, **kwargs):
        ax = ax or plt.gca()
        kwargs.setdefault('ls', '')
        kwargs.setdefault('marker', 's')
        kwargs.setdefault('capsize', 5)

        return ax.errorbar(
            x=self.x,
            y=self.y,
            xerr=self.xerr,
            yerr=self.yerr,
            **kwargs
        )
