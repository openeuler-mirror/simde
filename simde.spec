%global commit_munit da8f73412998e4f1adf1100dc187533a51af77fd
%global commit_simde 3378ab337698933ccb2e4068b26acd5c6afe27c5
%global hedley_version 14
%global debug_package %{nil}

Name:          simde
Version:       0.7.3
Release:       1
Summary:       Implementations of SIMD instruction sets for systems which don't natively support them
License:       MIT and CC0-1.0
URL:           https://github.com/nemequ/simde
Source0:       https://github.com/simd-everywhere/%{name}/archive/%{commit_simde}.tar.gz
Source1:       https://github.com/nemequ/munit/archive/%{commit_munit}.tar.gz
BuildRequires: clang
BuildRequires: cmake
BuildRequires: gcc
BuildRequires: gcc-c++

# simde/hedley.h
# https://github.com/nemequ/hedley
Provides: bundled(hedley) = %{hedley_version}

%description
%{summary}
The SIMDe header-only library provides fast, portable implementations of SIMD
intrinsics on hardware which doesn't natively support them, such as calling
SSE functions on ARM. There is no performance penalty if the hardware supports
the native implementation (e.g., SSE/AVX runs at full speed on x86,
NEON on ARM, etc.).

%package devel
Summary: Header files for SIMDe development
Provides: %{name}-static = %{version}-%{release}

%description devel
The simde-devel package contains the header files needed
to develop programs that use the SIMDe.

%prep
%autosetup -n %{name}-%{commit_simde} -p1

%build

%install
mkdir -p %{buildroot}%{_includedir}
cp -a simde %{buildroot}%{_includedir}

%check
# Check version.
version_major=$(grep '^#define SIMDE_VERSION_MAJOR ' simde/simde-common.h | cut -d ' ' -f 3)
version_minor=$(grep '^#define SIMDE_VERSION_MINOR ' simde/simde-common.h | cut -d ' ' -f 3)
version_micro=$(grep '^#define SIMDE_VERSION_MICRO ' simde/simde-common.h | cut -d ' ' -f 3)
test "%{version}" = "${version_major}.${version_minor}.${version_micro}"

for file in $(find simde/ -type f); do
  if ! [[ "${file}" =~ \.h$ ]]; then
    echo "${file} is not a header file."
    false
  elif [ -x "${file}" ]; then
    echo "${file} has executable bit."
    false
  fi
done

rm -rf test/munit
tar xzvf %{SOURCE1}
mv munit-%{commit_munit} test/munit

echo "== 1. tests on gcc =="
gcc --version
g++ --version

echo "=== 1.1. tests on gcc without flags ==="
mkdir test/build-gcc
pushd test/build-gcc
CC=gcc CXX=g++ cmake ..
%make_build
./run-tests
popd

echo "=== 1.2. tests on gcc with flags ==="
mkdir test/build-gcc-with-flags
pushd test/build-gcc-with-flags
CC=gcc CXX=g++ cmake \
  -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON \
  -DCMAKE_C_FLAGS="%{build_cflags}" \
  -DCMAKE_CXX_FLAGS="%{build_cxxflags}" \
  ..
%make_build
./run-tests
popd

%global toolchain clang
echo "== 2. tests on clang =="
clang --version
clang++ --version

echo "=== 2.1. tests on clang without flags ==="
mkdir test/build-clang
pushd test/build-clang
CC=clang CXX=clang++ cmake ..
%make_build
./run-tests
popd

echo "=== 2.2. tests on clang with flags ==="
mkdir test/build-clang-with-flags
pushd test/build-clang-with-flags

%ifnarch %{arm}
CC=clang CXX=clang++ cmake \
  -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON \
  -DCMAKE_C_FLAGS="%{build_cflags}" \
  -DCMAKE_CXX_FLAGS="%{build_cxxflags}" \
  ..
%make_build
./run-tests
%endif
popd

%files devel
%license COPYING
%doc README.md
%{_includedir}/%{name}

%changelog
* Tue Mar 8 2022 yaoxin <yaoxin30@huawei.com> - 0.7.3-1
- Upgrade simde to 0.7.3 to resolve compilation failures.

* Fri Jan 8 2021 chengzihan <chengzihan2@huawei.com> - 0.5.0-1
- Package init
