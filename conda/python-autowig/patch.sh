set -xe

if [[ -f windows.patch ]]; then
    rm windows.patch
fi
if [[ -f macosx.patch ]]; then
    rm macosx.patch
fi
if [[ -f travis-ci.patch ]]; then
    rm travis-ci.patch
fi

git ci -a -m "Prepare for new patches"

cd ../../test

git checkout -b generate_test_patch
sed -i'' -e '96,102d' test_basic.py
rm test_feedback.py
git diff > ../conda/python-autowig/windows.patch
git add test_feedback.py test_basic.py
git commit -m 'patch generated'
git checkout master
git branch -D generate_test_patch

git checkout -b generate_test_patch
rm test_feedback.py
git diff > ../conda/python-autowig/macosx.patch
rm test_subset.py
git diff > ../conda/python-autowig/travis-ci.patch
git add test_feedback.py test_subset.py
git commit -m 'patch generated'
git checkout master
git branch -D generate_test_patch

cd ../conda/python-autowig
git add windows.patch macosx.patch travis-ci.patch
git ci -a -m "Add new patches"