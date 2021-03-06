# -*- coding: utf-8 -*-
#APIDOC["Path"]=/Core/Signal
#APIDOC["Draft"]=False
#--end--
"""
The module only contains the function "detect_onset" implemenented by Marcos Duarte, available in [BMC](https://github.com/demotu/BMC)

see BMC documentation for details

"""

import numpy as np

__author__ = 'Marcos Duarte, https://github.com/demotu'
__version__ = "1.0.7"
__license__ = "MIT"


def detect_onset(x, threshold=0, n_above=1, n_below=0,
                 threshold2=None, n_above2=1, show=False, ax=None):
    """Detects onset in data based on amplitude threshold.
    """

    x = np.atleast_1d(x).astype('float64')
    # deal with NaN's (by definition, NaN's are not greater than threshold)
    x[np.isnan(x)] = -np.inf
    # indices of data greater than or equal to threshold
    inds = np.nonzero(x >= threshold)[0]
    if inds.size:
        # initial and final indexes of almost continuous data
        inds = np.vstack((inds[np.diff(np.hstack((-np.inf, inds))) > n_below+1],
                          inds[np.diff(np.hstack((inds, np.inf))) > n_below+1])).T
        # indexes of almost continuous data longer than or equal to n_above
        inds = inds[inds[:, 1]-inds[:, 0] >= n_above-1, :]
        # minimum amplitude of n_above2 values in x to detect
        if threshold2 is not None and inds.size:
            idel = np.ones(inds.shape[0], dtype=bool)
            for i in range(inds.shape[0]):
                if np.count_nonzero(x[inds[i, 0]: inds[i, 1]+1] >= threshold2) < n_above2:
                    idel[i] = False
            inds = inds[idel, :]
    if not inds.size:
        inds = np.array([])  # standardize inds shape for output
    if show and x.size > 1:  # don't waste my time ploting one datum
        _plot(x, threshold, n_above, n_below, threshold2, n_above2, inds, ax)

    return inds


def _plot(x, threshold, n_above, n_below, threshold2, n_above2, inds, ax):
    """Plot results of the detect_onset function, see its help."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print('matplotlib is not available.')
    else:
        if ax is None:
            _, ax = plt.subplots(1, 1, figsize=(8, 4))

        if inds.size:
            for (indi, indf) in inds:
                if indi == indf:
                    ax.plot(indf, x[indf], 'ro', mec='r', ms=6)
                else:
                    ax.plot(range(indi, indf+1), x[indi:indf+1], 'r', lw=1)
                    ax.axvline(x=indi, color='b', lw=1, ls='--')
                ax.axvline(x=indf, color='b', lw=1, ls='--')
            inds = np.vstack((np.hstack((0, inds[:, 1])),
                              np.hstack((inds[:, 0], x.size-1)))).T
            for (indi, indf) in inds:
                ax.plot(range(indi, indf+1), x[indi:indf+1], 'k', lw=1)
        else:
            ax.plot(x, 'k', lw=1)
            ax.axhline(y=threshold, color='r', lw=1, ls='-')

        ax.set_xlim(-.02*x.size, x.size*1.02-1)
        ymin, ymax = x[np.isfinite(x)].min(), x[np.isfinite(x)].max()
        yrange = ymax - ymin if ymax > ymin else 1
        ax.set_ylim(ymin - 0.1*yrange, ymax + 0.1*yrange)
        ax.set_xlabel('Data #', fontsize=14)
        ax.set_ylabel('Amplitude', fontsize=14)
        if threshold2 is not None:
            text = 'threshold=%.3g, n_above=%d, n_below=%d, threshold2=%.3g, n_above2=%d'
        else:
            text = 'threshold=%.3g, n_above=%d, n_below=%d, threshold2=%r, n_above2=%d'
        ax.set_title(text % (threshold, n_above,
                             n_below, threshold2, n_above2))
        # plt.grid()
        plt.show()
