"""Run all tests."""
if True:
    import test_update
    import test_block_ancestry_funcs
    import test_brenthy_api
    import test_brenthy_logs
    import test_walytis_beta
    import test_walytis_block_sync_1
    import test_walytis_beta_quick
    import test_walytis_block_sync_2
    import testing_utils
    from brenthy_docker import build_docker_image

if __name__ == "__main__":
    build_docker_image(verbose=False)

    test_update.REBUILD_DOCKER = False
    test_walytis_beta.REBUILD_DOCKER = False
    test_walytis_block_sync_1.REBUILD_DOCKER = False
    test_walytis_block_sync_2.REBUILD_DOCKER = False

    testing_utils.BREAKPOINTS = False

    test_update.run_tests()
    test_brenthy_api.run_tests()
    test_walytis_beta_quick.run_tests()
    test_walytis_beta.run_tests()
    test_walytis_block_sync_1.run_tests()
    test_walytis_block_sync_2.run_tests()
    test_block_ancestry_funcs.run_tests()
    test_brenthy_logs.run_tests()
