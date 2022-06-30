To release version x.y.z of git-keeper, follow the steps below.

### GitHub

* Update the `VERSION` file with the new version number.
* Run `bump_version.py` to propagate the new version number to all
  packages
* Merge the newly versioned code with the `develop` branch via pull
  request
* Merge the `develop` branch with the `master` branch via pull request
* Create an annotated tag on the `master` branch like so:
  `git tag -a x.y.z -m "Version x.y.z"`
* Push the tag directly to the master branch with `git push --tags`
* Create a new release on GitHub from the new tag.

### PyPI

Follow the [official packaging documentation](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
to build and upload all 3 packages to PyPI.
