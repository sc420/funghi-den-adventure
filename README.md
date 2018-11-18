# Funghi's Den Adventure Assignment Calculator

It calculates best funghis to use in single or multiple adventures.

It has the following additional features:

* You can specify the importance of rewards
* You can limit the number of possible assignment outputs
* You can build your own programs with the help of existing functions easily

## Requirements

1. [Python 3.7](https://www.anaconda.com/download/)
2. `pyyaml` package (Type `pip install pyyaml` to install)

## How to Use

1. Edit `data/all/funghis.yaml`
2. Run one of the following examples

Or create your own `funghis.yaml` and change the value of `--funghis_path` to the path.

## Specifications

See comments in `data/all/*.yaml`.

## Examples

### Single Adventure

`calc_single.py` calculates best allocations for single adventure. The default maximum number of allocation outputs is 10, use `--max` to adjust.

```shell
python calc_single.py --data_dir=data/1-鼴鼠之洞-入口 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/2-鼴鼠之洞-中途 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/3-岩石隧道-入口 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/4-岩石隧道-中途 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/5-黏液地底湖-入口 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/6-黏液地底湖-中途 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/7-咕嚕咕嚕間歇泉-入口 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/8-咕嚕咕嚕間歇泉-中途 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/9-螢火蟲之路-入口 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/10-螢火蟲之路-中途 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/11-樹根隧道-入口 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/12-樹根隧道-中途 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/13-清涼結冰洞-筆直通道 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/14-清涼結冰洞-凹凸通道 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/15-清涼結冰洞-光滑通道 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/16-砂牆空洞-沙沙通道 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/17-砂牆空洞-隆起通道 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/18-砂牆空洞-厚重通道 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/19-灼熱熔岩窟-咕嘟咕嘟區 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/20-灼熱熔岩窟-滾燙滾燙區 --funghis_path=data/all/funghis.yaml
```

### Compatible Allocations

`calc_compatible.py` calculates the same allocation which can be used for multiple adventures and achieve best score. The default maximum number of allocation outputs is 10, use `--max` to adjust.

```shell
python calc_compatible.py --data_dirs=data/1-鼴鼠之洞-入口,data/2-鼴鼠之洞-中途 --funghis_path=data/all/funghis.yaml
python calc_compatible.py --data_dirs=data/3-岩石隧道-入口,data/4-岩石隧道-中途 --funghis_path=data/all/funghis.yaml
python calc_compatible.py --data_dirs=data/5-黏液地底湖-入口,data/6-黏液地底湖-中途 --funghis_path=data/all/funghis.yaml
python calc_compatible.py --data_dirs=data/7-咕嚕咕嚕間歇泉-入口,data/8-咕嚕咕嚕間歇泉-中途 --funghis_path=data/all/funghis.yaml
python calc_compatible.py --data_dirs=data/9-螢火蟲之路-入口,data/10-螢火蟲之路-中途 --funghis_path=data/all/funghis.yaml
python calc_compatible.py --data_dirs=data/11-樹根隧道-入口,data/12-樹根隧道-中途 --funghis_path=data/all/funghis.yaml
python calc_compatible.py --data_dirs=data/13-清涼結冰洞-筆直通道,data/14-清涼結冰洞-凹凸通道,data/15-清涼結冰洞-光滑通道 --funghis_path=data/all/funghis.yaml
python calc_compatible.py --data_dirs=data/16-砂牆空洞-沙沙通道,data/17-砂牆空洞-隆起通道,data/18-砂牆空洞-厚重通道 --funghis_path=data/all/funghis.yaml
```

### Global Allocations

`calc_global.py` calculates best allocations for multiple adventures without specifying duplicated funghis. The former adventures in `--data_dirs` will be allocated first. This default maximum number of allocation outputs is 1, use `--max` to adjust.

```shell
python calc_global.py --data_dirs=data/18-砂牆空洞-厚重通道,data/15-清涼結冰洞-光滑通道,data/12-樹根隧道-中途,data/10-螢火蟲之路-中途,data/8-咕嚕咕嚕間歇泉-中途,data/6-黏液地底湖-中途,data/4-岩石隧道-中途,data/2-鼴鼠之洞-中途 --funghis_path=data/all/funghis.yaml
```
