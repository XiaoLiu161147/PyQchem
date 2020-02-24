from pyqchem.qchem_core import get_output_from_qchem
from pyqchem.qc_input import QchemInput
from pyqchem.structure import Structure
from pyqchem.parsers.parser_rasci import rasci as parser_rasci
from pyqchem.basis import get_basis_from_ccRepo, trucate_basis, basis_to_txt
import numpy as np

# create molecule
molecule = Structure(coordinates=[[0.0, 0.0, 0.0000],
                                  [0.0, 0.0, 1.5811]],
                     atomic_elements=['Se', 'H'],
                     charge=-1,
                     multiplicity=1)

# Generate basis name list
basis_name_list = []
for s1 in ['cc-pV_Z', 'cc-pCV_Z']:
    for s2 in ['D', 'T', 'Q', '5']:
        basis_name_list.append(s1.replace('_', s2))


for calc_soc in [1, 2]:
    for basis_name in basis_name_list:
        print('basis:', basis_name)
        for active_space in [[3, 2, 16], [5, 3, 15], [7, 4, 14], [17, 9, 9]]:
            basis_custom_repo = get_basis_from_ccRepo(molecule, 
                                                      basis_name,
                                                      if_missing=basis_name.replace('cc-pC', 'cc-p'))
            basis_custom_repo = trucate_basis(basis_custom_repo,
                                              shells=['G', 'H', 'I', 'J', 'K'])


            qc_input = QchemInput(molecule,
                                  jobtype='sp',
                                  exchange='hf',
                                  correlation='rasci',
                                  purecart='1111',
                                  unrestricted='False',
                                  thresh=14,
                                  scf_convergence=8,
                                  max_cis_cycles=150,
                                  basis=basis_custom_repo,
                                  ras_elec=active_space[0],
                                  ras_act=active_space[1],
                                  ras_occ=active_space[2],
                                  ras_spin_mult=0,
                                  ras_roots=2,      # calculate 8 states
                                  ras_do_hole=False,
                                  ras_do_part=False,
                                  calc_soc=calc_soc,
                                  set_iter=30,
                                  mem_total=15000,
                                  # mem_static=900
                                  )

            # print(qc_input.get_txt())
            output, _ = get_output_from_qchem(qc_input,
                                              processors=10,
                                              force_recalculation=False,
                                              parser=parser_rasci,
                                              store_full_output=True
                                              )

            # print(output)
            # print(_)
            # print(output['interstate_properties'])
            try:
                gamma_total = output['interstate_properties'][(1, 2)]['gamma_total']
                soc_1e = np.array(output['interstate_properties'][(1, 2)]['1e_soc_mat'])[0, 0]
                soc_2e = np.array(output['interstate_properties'][(1, 2)]['2e_soc_mat'])[0, 0]
                soc_tot = np.array(output['interstate_properties'][(1, 2)]['total_soc_mat'])[0, 0]
            except:
                print('---------------------------------------------')
                print('basis: {}'.format(basis_name))
                print('Active space (ele, act, occ): {}'.format(active_space))
                print('calc_soc: {}'.format(calc_soc))
                print('calculation_failed')
                continue

            print('---------------------------------------------')
            print('basis: {}'.format(basis_name))
            print('Active space (ele, act, occ): {}'.format(active_space))
            print('calc_soc: {}'.format(calc_soc))
            print('gamma_tot: {}'.format(gamma_total))
            print('soc_1e  {0.real: 10.3f} + {0.imag: 10.8f}i'.format(soc_1e))
            print('soc_2e  {0.real: 10.3f} + {0.imag: 10.8f}i'.format(soc_2e))
            print('soc_tot {0.real: 10.3f} + {0.imag: 10.8f}i'.format(soc_tot))