"""Run all tests."""
if True:
    import test_update
    import test_brenthy_api
    import test_brenthy_logs
    import testing_utils
    from brenthy_docker import build_docker_image

if __name__ == "__main__":
    build_docker_image(verbose=False)

    test_update.REBUILD_DOCKER = False

    testing_utils.BREAKPOINTS = False

    test_update.run_tests()
    test_brenthy_api.run_tests()
    test_brenthy_logs.run_tests()
