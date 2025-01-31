import os
import numpy as np
from utils.np import psvfn
import matplotlib.pyplot as plt
from libs.basicIO import pathBIO
from utils.preprocessing.timeseries.basicTS import smoothing as smoothing_function

class Plot1D:
    """
    Example:[inside args.yaml]
        plot: plot1D:neon
        plot: plot1D:@dark_background
        plot: plot1D:@Solarize_Light2
        plot: plot1D:@ggplot
    """
    def __init__(self, xlabel='x', ylabel='y', color='#D9D9D9', font=None, title_fontdict=None, labels_fontdict=None, grid_args_dict=None, mplstyle=None):
        self.mplstyle = str('neon' if mplstyle is None else mplstyle)
        self.title_fontdict = title_fontdict if title_fontdict else dict(family=[font, 'Purisa', 'sans-serif', 'serif'], color=color, weight='ultralight')
        self.labels_fontdict = labels_fontdict if labels_fontdict else dict(family=[font, 'Purisa', 'sans-serif', 'serif'], color=color, weight='bold', fontsize='x-large')
        self.grid_args_dict = grid_args_dict if grid_args_dict else dict(zorder=0.5, alpha=.02, color=color)

        if self.mplstyle.startswith('@'):
            style = self.mplstyle[1:]
        else:
            style = pathBIO('//utils/plots/style/{}.mplstyle'.format(self.mplstyle))
        plt.style.use(style)
        self.fig = plt.figure(figsize=(6, 4), facecolor=None)
        # self.fig.patch.set_alpha(.08)
        # plt.suptitle('suptitle', fontdict=self.title_fontdict)
        # plt.title('title', fontdict=self.title_fontdict)
        
        self.labels_fontdict = {}
        plt.xlabel(xlabel, fontdict=self.labels_fontdict)
        plt.ylabel(ylabel, fontdict=self.labels_fontdict)
        plt.grid(**self.grid_args_dict)
        plt.xticks(fontname=font)
        plt.yticks(fontname=font)
    
    def plot_metrics(self, db, hash, col_names, index=0, label='', tbl='', plt_show=True, smoothing=True, smooth_dpi=300, smooth_k=3, smooth_both=False):
        from libs.coding import sha1
        from libs.dbms.sqlite_dbms import SqliteDBMS
        sqlite_dbms = SqliteDBMS(db)
        table_names = sqlite_dbms.get_tables()
        
        data = []
        for tbl_name in table_names:
            cols = sqlite_dbms.get_colnames(tbl_name)
            for di in ['step', 'timestamp']:
                if di in cols:
                    cols.remove(di)
            cols = [c.replace('__', '/') for c in cols]
            reconstructrd_hash = sha1(' | '.join(sorted(list(cols))))
            # print(tbl, tbl_name, tbl.lower() in tbl_name.lower())
            if (reconstructrd_hash == hash) and (tbl.lower() in tbl_name.lower()):
                partial_data = sqlite_dbms.select('select {} from {}'.format(col_names, tbl_name))
                data = data + partial_data

        D = list(map(list, zip(*data)))
        X, Y = range(len(D[index])), D[index]
        if smoothing and smooth_both:
            if label:
                label = label + '-'
            self.plot(X, Y, label=f'{label}smooth', plt_show=False, smoothing=True, smooth_dpi=smooth_dpi, smooth_k=smooth_k)
            self.plot(X, Y, label=f'{label}sharp', plt_show=plt_show, smoothing=False, smooth_dpi=smooth_dpi, smooth_k=smooth_k)
        else:
            self.plot(X, Y, label=label, plt_show=plt_show, smoothing=smoothing, smooth_dpi=smooth_dpi, smooth_k=smooth_k)
    
    def savefig(self, path, dpi=1200, bbox_inches='tight', **kwargs):
        dstpath = pathBIO(path)
        os.makedirs(os.path.split(dstpath)[0], exist_ok=True)
        savefig_result = self.fig.savefig(dstpath, dpi=dpi, bbox_inches=bbox_inches, **kwargs)
        plt.close(self.fig)
        return savefig_result

    def plot(self, x=None, y=None, ax=None, label=None, plt_show=False, smoothing=False, smooth_k=3, smooth_dpi=300, ffty=False, ffty_div2N=False, passive_fn=None):
        if (x is None) and (not (y is None)):
            x = range(y.shape[0])
        assert (not ((x is None) or (y is None))), '`x`, `y` both of this must be `not None` | (`x` is `None` == `{}`) | (`y` is `None` == `{}`)'.format(x is None, y is None)
        
        if ffty:
            y = np.fft.fft(y)
            if ffty_div2N:
                y = y / y.shape[0]
        
        y = psvfn(y, passive_fn)
        
        if ax is None:
            ax = self.fig.gca() # ax = plt.gca()
        # ax.patch.set_facecolor('#3498db')
        # ax.patch.set_alpha(.08)
        # y_ticks=['y tick 1','y tick 2','y tick 3']
        # ax.set_yticklabels(y_ticks, rotation=0, fontsize=8)
        x = np.array(x)
        y = np.array(y)
        if smoothing:
            x, y = smoothing_function(x, y, smooth_dpi=smooth_dpi, smooth_k=smooth_k)
        
        line, = ax.plot(x, y, lw=1, zorder=6, label=label)
        for cont in range(6, 1, -1):
            ax.plot(x, y, lw=cont, color=line.get_color(), zorder=5, alpha=0.05)
        ax.legend()
        if plt_show:
            plt.show()
        return ax     
        

if __name__ == '__main__':
    neon = Plot1D(xlabel='x1', ylabel='y1')
    neon2 = Plot1D(xlabel='x2', ylabel='y2')
    x = np.linspace(0, 4, 100)
    y = np.sin(np.pi*x + 1e-6)/(np.pi*x + 1e-6)
    for cont in range(5):
        neon.plot(x, y/(cont + 1), label=f'f({cont})')
        neon2.plot(x, -y/(cont + 1))
    # neon.savefig('./neon_example1200.png')
    
    plt.show()

    # neon = Plot1D(xlabel='val-step', ylabel='val-loss')
    # neon2 = Plot1D(xlabel='val-step', ylabel='val-loss')
    # neon3 = Plot1D(xlabel='val-step', ylabel='val-loss')
    # neon.plot_metrics(
    #     hash = '5ee327ab28725a85bb9fcf6bd3a379052b659d9b',
    #     db = '/media/alihejrati/3E3009073008C83B/Code/Genie-ML/logs/vqgan/10/metrics2222.db',
    #     col_names = 'val__aeloss_step, step, epoch',
    #     smoothing=True,
    #     smooth_both=True,
    #     label='loss',
    #     plt_show=False
    # )
    # neon2.plot_metrics(
    #     hash = '5ee327ab28725a85bb9fcf6bd3a379052b659d9b',
    #     db = '/media/alihejrati/3E3009073008C83B/Code/Genie-ML/logs/vqgan/10/metrics2222.db',
    #     col_names = 'val__aeloss_step, step, epoch',
    #     plt_show=False
    # )
    # neon3.plot_metrics(
    #     hash = '5ee327ab28725a85bb9fcf6bd3a379052b659d9b',
    #     db = '/media/alihejrati/3E3009073008C83B/Code/Genie-ML/logs/vqgan/10/metrics2222.db',
    #     col_names = 'val__aeloss_step, step, epoch',
    #     smoothing=False
    # )