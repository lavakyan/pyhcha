#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np

from ase import Atoms
from maxvol_data import get_maxvol_polyhedron


def _get_topmost_pos(atoms):
    return atoms.positions[np.argmax(atoms.positions[:,2]),:]


def _get_topmost_nonO_pos(atoms):
    positions_nonO = \
        atoms.positions[np.array(atoms.get_chemical_symbols())!='O',:]
    return positions_nonO[np.argmax(positions_nonO[:,2]),:]


def _orient_to_z(atoms, pos_top=None, pos_center=None):
    '''
    rotate atoms to orient one of the O atoms to
    the top (towards Z coordinate)
    '''
    if pos_top is None:
        pos_top = _get_topmost_pos(atoms)

    if pos_center is None:
        pos_center = _get_topmost_nonO_pos(atoms)

    d = pos_top - pos_center
    rot_angle = np.arccos(d[2] / np.linalg.norm(d)) * 180 / np.pi
    if np.abs(rot_angle) > 1e-5:
        rot_axis = np.cross(d, [0,0,1])
        atoms.rotate(rot_angle, rot_axis, center=pos_center)
    return atoms


def get_polyhedron_atoms(n_verteces=4, R=2.75, A='Ba', O='O'):
    '''
    Construct perfect polyhedron

    n_verteces:
        number of verteces of the polyhedron
    R:
        distance between central atom to O atoms
    A:
        type of the central atom
    O:
        type of surrounding atoms
    '''
    atoms = Atoms(A)
    coords = get_maxvol_polyhedron(n_verteces)
    atoms.extend(
        Atoms(f'{O}{n_verteces}', positions=R * np.array(coords)))
    return atoms


def _add_bridged_polyhedron(atoms, n_verteces=4, R=2.75, phi1=45, theta=122, phi2=0, A='Ba'):
    '''
    add segment to a chain of polyhedra
    '''
    pos_bridge = _get_topmost_pos(atoms)
    pos_C = _get_topmost_nonO_pos(atoms)

    fragment = get_polyhedron_atoms(n_verteces=n_verteces, R=R, A=A)
    fragment = _orient_to_z(fragment)

    fragment.pop(np.argmax(fragment.positions[:,2]))  # remove top O
    fragment.rotate(180, [1,0,0])  # flip O vacancy down
    fragment.translate(pos_C-fragment.positions[0,:])  # 0th is nonO
    fragment.translate([0, 0, R])
    fragment.rotate(phi1, [0,0,1], center=pos_C)
    fragment.rotate(180-theta, [1,0,0], center=pos_C)
    fragment.translate([0, 0, R])
    pos_Cnext = fragment.positions[0,:]
    d = pos_Cnext - pos_bridge
    fragment.rotate(phi2-phi1, d, center=pos_Cnext)
    pos_Cnext = fragment.positions[0,:]
    atoms.extend(fragment)
    atoms = _orient_to_z(atoms, pos_Cnext, pos_bridge)
    return atoms


def gen_polyhedra_chain(n_verteces=4, n_segments=3, R=2.75, phi1=45, theta=122, phi2=0, A='Ba'):
    '''
    Parameters:

    n_verteces:
        number of verteces of the polyhedron
    n_segments:
        number of polyhedrons in the chain
    R:
        distance between central atom to O atoms
    phi1, phi2:
        rotational angles
    theta:
        chain bend angle
    A:
        type of the central atom
    '''

    atoms = get_polyhedron_atoms(n_verteces=n_verteces, R=R, A=A)
    atoms = _orient_to_z(atoms)

    for _ in range(n_segments-1):
        #print('next segment')
        atoms = _add_bridged_polyhedron(atoms=atoms,
                                        n_verteces=n_verteces,
                                        R=R, phi1=phi1,
                                        theta=theta, phi2=phi2, A=A)

    return atoms


if __name__ == '__main__':

    atoms = gen_polyhedra_chain(n_verteces=6, n_segments=4,
                                R=2.75, phi1=0, theta=120, phi2=0,
                                A='Ba')

    from ase.visualize import view
    view(atoms)




print('See you!')

