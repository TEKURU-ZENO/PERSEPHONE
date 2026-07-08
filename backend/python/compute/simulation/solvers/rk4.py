# Standard Runge-Kutta 4th Order Integrator

def rk4_step(f, t, y, dt, *args):
  """
  Performs a single RK4 step.
  f: function calculating derivatives dy/dt = f(t, y, *args)
  t: current time
  y: current state vector (as list)
  dt: time step size
  """
  k1 = f(t, y, *args)
  
  y_k2 = [y[i] + k1[i] * dt / 2.0 for i in range(len(y))]
  k2 = f(t + dt / 2.0, y_k2, *args)
  
  y_k3 = [y[i] + k2[i] * dt / 2.0 for i in range(len(y))]
  k3 = f(t + dt / 2.0, y_k3, *args)
  
  y_k4 = [y[i] + k3[i] * dt for i in range(len(y))]
  k4 = f(t + dt, y_k4, *args)
  
  new_y = [
    y[i] + (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]) * dt / 6.0
    for i in range(len(y))
  ]
  return new_y
