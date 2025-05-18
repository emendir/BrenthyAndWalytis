"""Run all tests."""
import _testing_utils
import test_block_ancestry_funcs
import test_walytis_beta
import test_walytis_block_sync_1
import test_walytis_beta_quick
import test_walytis_block_sync_2

from build_docker import build_docker_image
if __name__ == "__main__":
    build_docker_image(verbose=False)

    test_walytis_beta.REBUILD_DOCKER = False
    test_walytis_block_sync_1.REBUILD_DOCKER = False
    test_walytis_block_sync_2.REBUILD_DOCKER = False

    _testing_utils.BREAKPOINTS = False
    _testing_utils.PYTEST = False

    test_walytis_beta_quick.run_tests()
    test_walytis_beta.run_tests()
    test_walytis_block_sync_1.run_tests()
    test_walytis_block_sync_2.run_tests()
    test_block_ancestry_funcs.run_tests()
    
    _testing_utils.terminate()
