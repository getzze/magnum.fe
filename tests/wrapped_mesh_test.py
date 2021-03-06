import unittest
from magnumfe import *
import numpy

set_log_active(False)

complete_mesh = Mesh("mesh/wrapped_1.xml.gz")
mesh = WrappedMesh.create(complete_mesh, 1)

class WrappedMeshTest(unittest.TestCase):

  def test_different_sizes(self):
    assert mesh.size(0) < mesh.with_shell.size(0)

  def test_cut(self):
    V    = FunctionSpace(mesh.with_shell, "Lagrange", 2)
    expr = Expression("sin(x[0])")
    f    = interpolate(expr, V)


    f_cut = mesh.cut(f)
    
    self.assertOnSuperMesh(f)
    self.assertOnSubMesh(f_cut)

    self.assertEqualAtPoint(f, f_cut, (0.1, 0.2, 0.3))
    self.assertEqualAtPoint(f, f_cut, (0.3, 0.5, 0.8))
    self.assertEqualAtPoint(f, f_cut, (-0.1, -0.2, 0.3))

  def test_expand(self):
    V    = FunctionSpace(mesh, "Lagrange", 2)
    expr = Expression("sin(x[0])")
    f    = interpolate(expr, V)

    f_expanded = mesh.expand(f)
    
    self.assertOnSubMesh(f)
    self.assertOnSuperMesh(f_expanded)

    self.assertEqualAtPoint(f, f_expanded, (0.1, 0.2, 0.3))
    self.assertEqualAtPoint(f, f_expanded, (0.3, 0.5, 0.8))
    self.assertEqualAtPoint(f, f_expanded, (-0.1, -0.2, 0.3))
    self.assertZeroAtPoint(f_expanded, (1.6, 1.6, 1.6))
    self.assertZeroAtPoint(f_expanded, (-1.6, -1.6, -1.6))

  def test_expand_dont_overwrite(self):
    V    = FunctionSpace(mesh, "Lagrange", 2)
    expr = Expression("sin(x[0])")
    f    = interpolate(expr, V)

    V_complete = FunctionSpace(complete_mesh, "Lagrange", 2)
    f_complete = interpolate(Constant(2.0), V_complete)

    f_expanded = mesh.expand(f, f_complete)
    self.assertEqualAtPoint(f, f_expanded, (0.1, 0.2, 0.3))
    self.assertEqualAtPoint(f, f_expanded, (0.3, 0.5, 0.8))
    self.assertEqualAtPoint(f, f_expanded, (-0.1, -0.2, 0.3))
    self.assertValueAtPoint(f_expanded, (1.6, 1.6, 1.6), 2.0)
    self.assertValueAtPoint(f_expanded, (-1.6, -1.6, -1.6), 2.0)


  def test_multiple_subdomains(self):
    complete_mesh = Mesh("mesh/wrapped_2.xml.gz")

    mesh1 = WrappedMesh.create(complete_mesh, 1)
    mesh3 = WrappedMesh.create(complete_mesh, 3)
    mesh13 = WrappedMesh.create(complete_mesh, (1,3))

    self.assertEqual(mesh13.size(3), mesh1.size(3) + mesh3.size(3))

  def test_multiple_subdomains_inverted(self):
    mesh1 = WrappedMesh.create(mesh.with_shell, (1000,1001,1002,1003), invert=True)
    self.assertEqual(mesh.size(3), mesh1.size(3))

  def assertEqualAtPoint(self, f1, f2, point):
    v1 = numpy.zeros((1,), dtype="d")
    v2 = numpy.zeros((1,), dtype="d")
    f1.eval(v1, numpy.array(point))
    f2.eval(v2, numpy.array(point))
    self.assertAlmostEqual(v1[0], v2[0])

  def assertValueAtPoint(self, f, point, value = 0.0):
    v = numpy.zeros((1,), dtype="d")
    f.eval(v, numpy.array(point))
    self.assertAlmostEqual(value, v[0])

  def assertZeroAtPoint(self, f, point):
    self.assertValueAtPoint(f, point, 0.0)

  def assertOnSuperMesh(self, f):
    self.assertEqual(mesh.with_shell.size(0), f.function_space().mesh().size(0))

  def assertOnSubMesh(self, f):
    self.assertEqual(mesh.size(0), f.function_space().mesh().size(0))

if __name__ == '__main__':
    unittest.main()
