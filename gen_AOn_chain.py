#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np

from ase import Atoms
from maxvol_data import get_maxvol_polyhedron



def orient_to_z(atoms):
    '''
    rotate atoms to orient one of the O atoms to
    the top (towards Z coordinate)
    '''
    i = np.argmax(atoms.positions[:,2])
    pos_O = atoms.positions[i,:]  # bridged oxygen - top

    positions_C = \
        atoms.positions[np.array(atoms.get_chemical_symbols())!='O',:]
    pos_C = positions_C[np.argmax(positions_C[:,2])]  # center of polyhedron

    d = pos_O - pos_C
    rot_angle = np.arccos(d[2] / np.linalg.norm(d)) * 180 / np.pi
    rot_axis = np.cross(d, [0,0,1])
    atoms.rotate(rot_angle, rot_axis, center=pos_C)
    return atoms


def get_polyhedron_atoms(n_verteces=4, R=2.75, A='Ba', O='O'):
    atoms = Atoms(A)
    coords = get_maxvol_polyhedron(n_verteces)
    atoms.extend(
        Atoms(f'{O}{n_verteces}', positions=R * np.array(coords)))
    return atoms


def add_bridged_polyhedron(atoms, n_verteces=4, R=2.75, phi1=45, theta=122, phi2=0, A='Ba'):
    '''
    todo
    '''
    pos_bridge = atoms.positions[np.argmax(atoms.positions[:,2]),:]
    #print(f'{pos_bridge=}')
    positions_nonO = \
        atoms.positions[np.array(atoms.get_chemical_symbols())!='O',:]
    pos_C = positions_nonO[np.argmax(positions_nonO[:,2])]
    #print(f'{pos_C=}')

    fragment = get_polyhedron_atoms(n_verteces=n_verteces, R=R, A=A)
    fragment = orient_to_z(fragment)

    fragment.pop(np.argmax(fragment.positions[:,2]))
    fragment.rotate(180, [1,0,0])  # flip Ovac down
    fragment.translate(pos_C-fragment.positions[0,:])
    fragment.translate([0, 0, R])
    fragment.rotate(phi1, [0,0,1], center=pos_C)
    fragment.rotate(180-theta, [1,0,0], center=pos_C)
    fragment.translate([0, 0, R])
    pos_next = fragment.positions[0,:]
    #print(f'{pos_next=}')
    d = pos_next - pos_bridge
    fragment.rotate(phi2-phi1, d, center=pos_next)
    atoms.extend(fragment)
    atoms = orient_to_z(atoms)
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
    atoms = orient_to_z(atoms)

    for _ in range(n_segments-1):
        #print('next segment')
        atoms = add_bridged_polyhedron(atoms=atoms,
                                       n_verteces=n_verteces,
                                       R=R, phi1=phi1,
                                       theta=theta, phi2=phi2, A=A)

    return atoms


if __name__ == '__main__':

    atoms = gen_polyhedra_chain(n_verteces=6, R=2.75, phi1=30, theta=120, phi2=30, A='Ba')
    print(atoms)
    from ase.visualize import view
    view(atoms)




print('See you!')

