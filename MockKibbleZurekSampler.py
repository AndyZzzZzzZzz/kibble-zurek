from dimod import SampleSet
from dwave.samplers import SimulatedAnnealingSampler
from dwave.system.temperatures import fluxbias_to_h
from dwave.system.testing import MockDWaveSampler

class MockKibbleZurekSampler(MockDWaveSampler):
    def __init__(
        self,
        nodelist=None,
        edgelist=None,
        properties=None,
        broken_nodes=None,
        broken_edges=None,
        topology_type='pegasus',
        topology_shape=[16],
        parameter_warnings=True,
        substitute_sampler=None,
        substitute_kwargs=None,
        exact_solver_cutoff=0,
    ):
        if substitute_sampler is None:
            substitute_sampler = SimulatedAnnealingSampler()
        if substitute_kwargs is None:
            substitute_kwargs = {'beta_range': [0, 3],
                                 'beta_schedule_type': 'linear',
                                 'num_sweeps': 100,
                                 'randomize_order': True,
                                 'proposal_acceptance_criteria': 'Gibbs'}
        super().__init__(
            nodelist=nodelist,
            edgelist=edgelist,
            properties=properties,
            broken_nodes=broken_nodes,
            broken_edges=broken_edges,
            topology_type=topology_type,
            topology_shape=topology_shape,
            parameter_warnings=parameter_warnings,
            substitute_sampler=substitute_sampler,
            substitute_kwargs=substitute_kwargs,
            exact_solver_cutoff=exact_solver_cutoff,
        )
        self.sampler_type = 'mock'
        self.mocked_parameters.add('annealing_time')

    def sample(self, bqm, **kwargs):

        # Extract flux biases from kwargs (if provided)
        flux_biases = kwargs.get('flux_biases', {})
        if flux_biases:
            # Remove flux_biases from kwargs to avoid passing it to substitute_sampler
            kwargs = kwargs.copy()
            del kwargs['flux_biases']

        annealing_time = kwargs.pop('annealing_time', None)
        if annealing_time is not None:
            try:
                num_sweeps = int(annealing_time * 1000)
            except (TypeError, ValueError):
                num_sweeps = 1000
            kwargs['annealing_time'] = num_sweeps
        else:
            # Default number of sweeps if annealing_time is not provided
            kwargs['annealing_time'] = kwargs.get('num_sweeps', 1000)

        # Adjust the BQM to include flux biases
        bqm_effective = bqm.change_vartype('SPIN', inplace=False)

        # flux_to_h_factor = fluxbias_to_h()
        # for v in bqm_effective.variables:
        #     bias = bqm_effective.get_linear(v)
        #     bqm_effective.set_linear(v, bias + flux_to_h_factor * flux_biases[v])

        ss = super().sample(bqm=bqm_effective, **kwargs)

        ss.change_vartype(bqm.vartype)

        ss = SampleSet.from_samples_bqm(ss, bqm)

        return ss

    def get_sampler(self):
        """
        Return the sampler instance.
        """
        return self
