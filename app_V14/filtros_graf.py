import numpy as np
from matplotlib.artist import Artist
from matplotlib.colors import LightSource

# --- Filtros para efectos ---
class BaseFilter:
    def get_pad(self, dpi): return 0
    def process_image(self, padded_src, dpi): raise NotImplementedError
    def __call__(self, im, dpi):
        pad = self.get_pad(dpi)
        padded_src = np.pad(im, [(pad, pad), (pad, pad), (0, 0)], "constant")
        tgt_image = self.process_image(padded_src, dpi)
        return tgt_image, -pad, -pad

class GaussianFilter(BaseFilter):
    def __init__(self, sigma, alpha=0.5, color=(0, 0, 0)):
        self.sigma, self.alpha, self.color = sigma, alpha, color
    def get_pad(self, dpi): return int(self.sigma * 3 / 72 * dpi)
    def process_image(self, padded_src, dpi):
        tgt_image = np.empty_like(padded_src)
        tgt_image[:, :, :3] = self.color
        tgt_image[:, :, 3] = smooth2d(padded_src[:, :, 3] * self.alpha, self.sigma / 72 * dpi)
        return tgt_image

class DropShadowFilter(BaseFilter):
    def __init__(self, sigma, alpha=0.3, color=(0, 0, 0), offsets=(0, 0)):
        self.gauss_filter = GaussianFilter(sigma, alpha, color)
        self.offsets = offsets
    def get_pad(self, dpi):
        return max(self.gauss_filter.get_pad(dpi), int(max(self.offsets) / 72 * dpi))
    def process_image(self, padded_src, dpi):
        t1 = self.gauss_filter.process_image(padded_src, dpi)
        a1 = np.roll(t1, int(self.offsets[0] / 72 * dpi), axis=1)
        a2 = np.roll(a1, -int(self.offsets[1] / 72 * dpi), axis=0)
        return a2
    
class LightFilter(BaseFilter):
    """Apply LightSource filter"""

    def __init__(self, sigma, fraction=1):
        """
        Parameters
        ----------
        sigma : float
            sigma for gaussian filter
        fraction: number, default: 1
            Increases or decreases the contrast of the hillshade.
            See `matplotlib.colors.LightSource`

        """
        self.gauss_filter = GaussianFilter(sigma, alpha=1)
        self.light_source = LightSource()
        self.fraction = fraction

    def get_pad(self, dpi):
        return self.gauss_filter.get_pad(dpi)

    def process_image(self, padded_src, dpi):
        t1 = self.gauss_filter.process_image(padded_src, dpi)
        elevation = t1[:, :, 3]
        rgb = padded_src[:, :, :3]
        alpha = padded_src[:, :, 3:]
        rgb2 = self.light_source.shade_rgb(rgb, elevation,
                                        fraction=self.fraction,
                                        blend_mode="overlay")
        return np.concatenate([rgb2, alpha], -1)

class FilteredArtistList(Artist):
    def __init__(self, artist_list, filter):
        super().__init__()
        self._artist_list, self._filter = artist_list, filter
    def draw(self, renderer):
        renderer.start_rasterizing()
        renderer.start_filter()
        for a in self._artist_list: a.draw(renderer)
        renderer.stop_filter(self._filter)
        renderer.stop_rasterizing()

def smooth1d(x, window_len):
    s = np.r_[2 * x[0] - x[window_len:1:-1], x, 2 * x[-1] - x[-1:-window_len:-1]]
    w = np.hanning(window_len)
    y = np.convolve(w / w.sum(), s, mode='same')
    return y[window_len - 1:-window_len + 1]

def smooth2d(A, sigma=3):
    window_len = max(int(sigma), 3) * 2 + 1
    A = np.apply_along_axis(smooth1d, 0, A, window_len)
    A = np.apply_along_axis(smooth1d, 1, A, window_len)
    return A
