"""Deterministic weighted L2 logistic models using NumPy and SciPy only."""
from __future__ import annotations
import numpy as np


def _sigmoid(z):
    z = np.asarray(z, dtype=float)
    tail = np.exp(-np.abs(z))
    return np.where(z >= 0, 1 / (1 + tail), tail / (1 + tail))


def fit_logistic(X, y, weights=None, l2=1.0) -> dict:
    """Fit a weighted logistic loss plus l2/2 times squared standardized slopes.

    Weights are normalized to mean one. The loss is summed, so l2=1 is a
    fixed Gaussian slope penalty whose relative strength decreases with data.
    The caller owns seed/family/arm balancing and the frozen train split.
    Degenerate single-class training returns a finite smoothed constant model.
    """
    from scipy.optimize import minimize

    X, y = np.asarray(X, dtype=float), np.asarray(y, dtype=float)
    if X.ndim != 2 or y.shape != (len(X),) or not len(X):
        raise ValueError('Expected nonempty 2-D X and one label per row')
    w = np.ones(len(X)) if weights is None else np.asarray(weights, dtype=float)
    if (w.shape != y.shape or not np.isfinite(X).all() or not np.isfinite(y).all()
            or not np.isfinite(w).all() or np.any(w < 0) or w.sum() <= 0
            or np.any((y != 0) & (y != 1)) or not np.isfinite(l2) or l2 < 0):
        raise ValueError('Invalid labels, nonnegative weights, features, or l2')
    # Zero-weight rows contribute neither normalization nor fitted statistics.
    w = w * (np.count_nonzero(w) / w.sum())
    mean = np.average(X, axis=0, weights=w)
    scale = np.sqrt(np.average((X - mean) ** 2, axis=0, weights=w))
    scale[scale < 1e-12] = 1.0
    Z = (X - mean) / scale
    successes, total = float(w @ y), float(w.sum())
    initial_probability = (successes + .5) / (total + 1.)
    theta = np.zeros(X.shape[1] + 1)
    theta[0] = np.log(initial_probability) - np.log1p(-initial_probability)
    constant = successes == 0 or successes == total

    def objective(t):
        z = t[0] + Z @ t[1:]
        residual = w * (_sigmoid(z) - y)
        loss = float(w @ (np.logaddexp(0, z) - y * z) + .5 * l2 * (t[1:] @ t[1:]))
        gradient = np.r_[residual.sum(), Z.T @ residual + l2 * t[1:]]
        return loss, gradient

    iterations, converged = 0, True
    if not constant:
        result = minimize(objective, theta, jac=True, method='L-BFGS-B',
                          options={'maxiter': 500, 'ftol': 1e-12, 'gtol': 1e-7,
                                   'maxls': 50})
        theta, iterations, converged = result.x, int(result.nit), bool(result.success)
        if not converged or not np.isfinite(theta).all():
            raise RuntimeError(f'Logistic optimization failed: {result.message}')
    return {'schema': 'public-logistic/v1', 'mean': mean.tolist(), 'scale': scale.tolist(),
            'intercept': float(theta[0]), 'coefficients': theta[1:].tolist(),
            'l2': float(l2), 'constant': bool(constant), 'converged': converged,
            'iterations': iterations, 'training_rows': int(len(X)),
            'positive_weight': successes, 'total_weight': total}


def predict(model: dict, X) -> np.ndarray:
    """Return finite Bernoulli probabilities for one row or a 2-D batch."""
    try:
        X = np.asarray(X, dtype=float)
        coefficients = np.asarray(model['coefficients'], dtype=float)
        mean = np.asarray(model['mean'], dtype=float)
        scale = np.asarray(model['scale'], dtype=float)
        intercept = np.asarray(model['intercept'], dtype=float)
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError('Invalid logistic asset or prediction input') from error
    if (coefficients.ndim != 1 or mean.shape != coefficients.shape
            or scale.shape != coefficients.shape or intercept.ndim != 0
            or not np.isfinite(coefficients).all() or not np.isfinite(mean).all()
            or not np.isfinite(scale).all() or np.any(scale <= 0)
            or not np.isfinite(intercept)):
        raise ValueError('Invalid logistic asset shape, values, or normalization scale')
    if X.ndim not in (1, 2) or X.shape[-1] != len(coefficients) or not np.isfinite(X).all():
        raise ValueError('Prediction feature shape or values are invalid')
    with np.errstate(over='ignore', invalid='ignore', divide='ignore'):
        logits = float(intercept) + ((X - mean) / scale) @ coefficients
    if not np.isfinite(logits).all():
        raise ValueError('Prediction arithmetic produced nonfinite logits')
    return _sigmoid(logits)
