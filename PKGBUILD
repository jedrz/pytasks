# Contributor: Lukasz Jedrzejewski <lukasz892 at gmail dot com>
pkgname=pytasks-git
pkgver=20110829
pkgrel=1
pkgdesc="A todo list with interval option"
arch=(any)
url="http://github.com/jedrz/pytasks"
license=('GPL')
depends=('python-gobject')
makedepends=('git')
md5sums=()

_gitname="pytasks"
_gitroot="git://github.com/jedrz/${_gitname}.git"

build() {
    cd "${srcdir}"
    msg "Connecting to GIT server...."
    if [ -d $_gitname ] ; then
        cd $_gitname && git pull origin
        msg "The local files are updated."
    else
        git clone $_gitroot
    fi
    msg "GIT checkout done or server timeout"

    msg "Starting make..."
    mkdir -p ${pkgdir}/usr/share/pytasks/
    cp -r ${srcdir}/pytasks/src/* ${pkgdir}/usr/share/pytasks/
    install -Dm 755 ${srcdir}/pytasks/pytasks ${pkgdir}/usr/bin/pytasks
}
