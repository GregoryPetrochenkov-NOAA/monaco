# test_gaussian_statistics.py

import pytest
from monaco.gaussian_statistics import sig2pct, pct2sig, conf_ellipsoid_sig2pct, conf_ellipsoid_pct2sig
from monaco.MCEnums import StatBound

def test_sig2pct():
    assert sig2pct(sig= 3, bound=StatBound.ONESIDED) == pytest.approx( 0.9986501)
    assert sig2pct(sig=-3, bound=StatBound.TWOSIDED) == pytest.approx(-0.9973002)

def test_pct2sig():
    assert pct2sig(p=0.0013499, bound=StatBound.ONESIDED) == pytest.approx(-3)
    assert pct2sig(p=0.9973002, bound=StatBound.TWOSIDED) == pytest.approx( 3)

def test_conf_ellipsoid_sig2pct():
    assert conf_ellipsoid_sig2pct(sig=3, df=1) == pytest.approx(0.9973002)
    assert conf_ellipsoid_sig2pct(sig=3, df=2) == pytest.approx(0.9888910)

def test_conf_ellipsoid_pct2sig():
    assert conf_ellipsoid_pct2sig(p=0.9973002, df=1) == pytest.approx(3)
    assert conf_ellipsoid_pct2sig(p=0.9888910, df=2) == pytest.approx(3)


### Inline Testing ###
# Can run here or copy into bottom of main file
def inline_testing():
    print(sig2pct(-3, bound=StatBound.TWOSIDED), sig2pct(3, bound=StatBound.ONESIDED)) # expected: -0.99730, 0.99865
    print(pct2sig(0.9973002, bound=StatBound.TWOSIDED), pct2sig(0.0013499, bound=StatBound.ONESIDED)) # expected: 3, -3
    print(conf_ellipsoid_sig2pct(3, df=1), conf_ellipsoid_sig2pct(3, df=2)) # expected: 0.99730, 0.98889
    print(conf_ellipsoid_pct2sig(0.9973002, df=1), conf_ellipsoid_pct2sig(0.988891, df=2)) # expected: 3.0, 3.0

if __name__ == '__main__':
    inline_testing()