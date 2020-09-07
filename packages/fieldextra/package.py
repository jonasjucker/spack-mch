# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install fieldextra
#
# You can edit this file again by typing:
#
#     spack edit fieldextra
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack import *
import subprocess


class Fieldextra(CMakePackage):
    """Fieldextra is a generic tool to manipulate NWP model data and gridded observations; simple data processing and more complex data operations are supported. Fieldextra is designed as a toolbox; a large set of primitive operations which can be arbitrarily combined are provided."""

    homepage = "http://www.cosmo-model.org/content/support/software/default.html"
    url      = "https://github.com/COSMO-ORG/fieldextra"
    git      = 'git@github.com:COSMO-ORG/fieldextra.git'
    maintainers = ['elsagermann']
    
    version('v13_2_2', commit='38a9f830ab15fb9f3b770173f63a3692a6a381a4')
    version('v13_2_0', commit='fe0a8b14314d7527168fd5684d89828bbd83ebf2')
    version('v13_1_0', commit='9649ec36dc36dfe3ef679a507f9a849dc2fdd452')
    
    variant('build_type', default='Optimized', description='Build type', values=('Optimized', 'Profiling', 'Debug'))
    variant('openmp', default=True)

    depends_on('libaec@1.0.0 ~build_shared_libs')
    depends_on('jasper@2.0.14: ~shared')
    depends_on('hdf5@1.8.21 +hl +fortran ~mpi')
    depends_on('zlib@1.2.11')
    depends_on('netcdf-c@4.4.0 ~mpi')
    depends_on('netcdf-fortran@4.4.4 ~shared ~mpi')
    depends_on('rttov@11.2.0')

    # parallelization
    depends_on('eccodes@2.18.0 build_type=Production jp2k=jasper +openmp', when='+openmp')
    depends_on('eccodes@2.18.0 build_type=Production jp2k=jasper ~openmp', when='~openmp')
    depends_on('icontools@2.4.3 +openmp', when='+openmp')
    depends_on('icontools@2.4.3 ~openmp', when='~openmp')
    depends_on('fieldextra-grib1@v13.2.2 +openmp', when='+openmp')
    depends_on('fieldextra-grib1@v13.2.2 ~openmp', when='~openmp')
    
    # optimization
    # optimized
    depends_on('icontools build_type=optimized', when='build_type=Optimized')
    depends_on('fieldextra-grib1 build_type=optimized', when='build_type=Optimized')

    # debug
    depends_on('icontools build_type=debug', when='build_type=Debug')
    depends_on('fieldextra-grib1 build_type=debug', when='build_type=Debug')

    # profiling
    depends_on('icontools build_type=debug', when='build_type=Profiling')
    depends_on('fieldextra-grib1 build_type=profiling', when='build_type=Profiling')


    def cmake_args(self):
        spec = self.spec

        args = []
        
        # needed to avoid conflicts with CMake Rpath settings
        args.append('-DCMAKE_BUILD_WITH_INSTALL_RPATH=1')
        args.append('-DRTTOV_VERSION={0}'.format(spec.format('{^rttov.version}')))

        if '~openmp' in spec:
            args.append('-DMULTITHREADED_BUILD=OFF')
        return args
    
    @run_after('install')
    @on_package_attributes(run_tests=True)
    def test(self):
        with working_dir('cookbook/support'):
            force_symlink('/store/s83/tsm/fieldextra/static/cookbook/input' ,'input')
        copy_tree(self.spec['eccodes'].prefix +'/bin', 'tools')
        copy_tree(self.spec['netcdf-c'].prefix +'/bin', 'tools')
        copy_tree(self.spec['netcdf-fortran'].prefix +'/bin', 'tools')
        force_symlink('/store/s83/tsm/fieldextra/static/cookbook/' + spec.format('{version}'), 'reference_cookbook')
        try:
            subprocess.run(['./cookbook/run.bash'])
        except:
            raise InstallError('Tests failed')
