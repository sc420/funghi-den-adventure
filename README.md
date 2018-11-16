# Funghi's Den Adventure Allocation Calculator

## Specifications

See comments in `data/all/*.yaml`.

## Requirements

1. [Python 3.7](https://www.anaconda.com/download/)

## Examples

### Single Adventure

The default maximum number of allocation outputs is 10, use `--max` to adjust.

```shell
python calc_single.py --data_dir=data/1-鼴鼠之洞-入口 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/2-鼴鼠之洞-中途 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/3-岩石隧道-入口 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/4-岩石隧道-中途 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/12-樹根隧道-中途 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/13-清涼結冰洞-筆直通道 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/14-清涼結冰洞-凹凸通道 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/15-清涼結冰洞-光滑通道 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/16-砂牆空洞-沙沙通道 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/17-砂牆空洞-隆起通道 --funghis_path=data/all/funghis.yaml
python calc_single.py --data_dir=data/18-砂牆空洞-厚重通道 --funghis_path=data/all/funghis.yaml
```

### All Allocations

`calc_all.py` calculates all allocations without specifying duplicated funghis. The former adventures in `--data_dirs` will be allocated first. This default maximum number of allocation outputs is 1, use `--max` to adjust.

```shell
python calc_all.py --data_dirs=data/18-砂牆空洞-厚重通道,data/15-清涼結冰洞-光滑通道,data/12-樹根隧道-中途 --funghis_path=data/all/funghis.yaml
```
