# must be run with root priviledges to perform uninstall

# get arguments passed to script:
install_dir=$1
data_dir=$2
python=$3

# Unregistering Brenthy as a service/background process
echo "Unregistering systemd service..."
systemctl stop brenthy
rm /etc/systemd/system/brenthy.service
systemctl daemon-reload

echo "Deleting user brenthy..."
# addsbrenthy user
deluser brenthy

# delete install_dir
echo "Deleting files..."
rm -r $install_dir

