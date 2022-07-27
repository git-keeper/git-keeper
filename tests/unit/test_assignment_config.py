import os

from gkeepcore.assignment_config import AssignmentConfig, TestEnv
import pytest

from gkeepcore.gkeep_exception import GkeepException


def test_non_existent_file():
    config = AssignmentConfig('not/a/path')

    assert config.env == TestEnv.FIREJAIL
    assert config.append_args is None
    assert config.image is None
    assert config.timeout is None
    assert config.memory_limit is None

    assert config.use_html is None
    assert config.announcement_subject == '[{class_name}] New assignment: {assignment_name}'
    assert config.results_subject == '[{class_name}] {assignment_name} test results'


def test_good_firejail_no_args():
    path = 'assignment_configs/good_firejail_no_args.cfg'
    assert os.path.isfile(path)

    config = AssignmentConfig(path)

    assert config.env == TestEnv.FIREJAIL
    assert config.append_args is None
    assert config.image is None
    assert config.timeout is None
    assert config.memory_limit is None

    assert config.use_html is None
    assert config.announcement_subject == '[{class_name}] New assignment: {assignment_name}'
    assert config.results_subject == '[{class_name}] {assignment_name} test results'


def test_good_firejail_append_args():
    path = 'assignment_configs/good_firejail_append_args.cfg'
    assert os.path.isfile(path)

    config = AssignmentConfig(path)

    assert config.env == TestEnv.FIREJAIL
    assert config.append_args == '--net=none --rlimit-fsize=10000'
    assert config.image is None
    assert config.timeout is None
    assert config.memory_limit is None

    assert config.use_html is None
    assert config.announcement_subject == '[{class_name}] New assignment: {assignment_name}'
    assert config.results_subject == '[{class_name}] {assignment_name} test results'


def test_good_default_firejail_all_other_options():
    path = 'assignment_configs/good_default_firejail_all_other_options.cfg'
    assert os.path.isfile(path)

    config = AssignmentConfig(path)

    assert config.env == TestEnv.FIREJAIL
    assert config.append_args is None
    assert config.image is None
    assert config.timeout == 30
    assert config.memory_limit == 1024

    assert config.use_html is False
    assert config.announcement_subject == 'New: {class_name} {assignment_name}'
    assert config.results_subject == 'Results: {class_name} {assignment_name}'


def test_good_docker():
    path = 'assignment_configs/good_docker.cfg'
    assert os.path.isfile(path)

    config = AssignmentConfig(path)

    assert config.env == TestEnv.DOCKER
    assert config.append_args is None
    assert config.image == 'docker_image'
    assert config.timeout is None
    assert config.memory_limit is None

    assert config.use_html is None
    assert config.announcement_subject == '[{class_name}] New assignment: {assignment_name}'
    assert config.results_subject == '[{class_name}] {assignment_name} test results'


def test_bad_firejail_has_image():
    path = 'assignment_configs/bad_firejail_has_image.cfg'
    assert os.path.isfile(path)

    with pytest.raises(GkeepException):
        AssignmentConfig(path)


def test_bad_docker_no_image():
    path = 'assignment_configs/bad_docker_no_image.cfg'
    assert os.path.isfile(path)

    with pytest.raises(GkeepException):
        AssignmentConfig(path)


def test_bad_docker_has_append_args():
    path = 'assignment_configs/bad_docker_has_append_args.cfg'
    assert os.path.isfile(path)

    with pytest.raises(GkeepException):
        AssignmentConfig(path)


def test_bad_tests_section_invalid_option():
    path = 'assignment_configs/bad_tests_section_invalid_option.cfg'
    assert os.path.isfile(path)

    with pytest.raises(GkeepException):
        AssignmentConfig(path)


def test_bad_email_section_invalid_option():
    path = 'assignment_configs/bad_email_section_invalid_option.cfg'
    assert os.path.isfile(path)

    with pytest.raises(GkeepException):
        AssignmentConfig(path)


def test_bad_invalid_section():
    path = 'assignment_configs/bad_invalid_section.cfg'
    assert os.path.isfile(path)

    with pytest.raises(GkeepException):
        AssignmentConfig(path)
