
import kaleido as kld
from tqdm import tqdm

### ARGSA
def argsA( parser ):

    parser.add_int( 'num_epochs' , d = 100 , h = 'Number of training epochs'                 )
    parser.add_int( 'eval_every' , d =   5 , h = 'Interval between epochs for evaluation'    )
    parser.add_int( 'plot_every' , d =   0 , h = 'Interval between evaluations for plotting' )

    parser.add_str( 'save' , d = None , h = 'Suffix for model to be saved'  )
    parser.add_str( 'load' , d = None , h = 'Suffix for model to be loaded' )

    parser.add_bol( 'train'   , d = False , h = 'Training or testing mode'  )
    parser.add_bol( 'restart' , d = False , h = 'Restart model to be saved' )

##### BASEA
class baseA:

######################################################

    ### POSTINIT
    def postInit( self , files = None , single_stats = False ):

        self.sess = kld.tf.Session()
        self.saver = kld.log.Saver( self.args.save_path , self.sess )
        if self.args.restart: self.saver.restart()
        self.loader = kld.log.Saver( self.args.load_path , self.sess )
        self.loader.restore_model( 'trained' )

        if self.args.train:
            if files is not None: self.saver.file( 'code' , files )
            self.saver.args( 'args' , self.args )

        self.single_stats = single_stats
        self.phase = 'training' if self.args.train else 'testing'
        self.width = max( 100 , len( self.display( self.args.eval_capt[0] , self.args.num_epochs ) ) + 4 )
        self.args.plot_every *= self.args.eval_every

######################################################

    ### LOOPBAR
    def loopBar( self , data , text , leave = True , enum = False ):
        bar = tqdm( data , '| ' + text + ' |' , ncols = self.width , leave = leave )
        return enumerate( bar ) if enum else bar

    ### LOOPOPTIM
    def loopOptim( self , data , epoch , leave = True , enum = False ):
        text = kld.dsp.count( 'Epoch' , epoch , self.args.num_epochs )
        return self.loopBar( range( data.num_batches() ) , text , leave , enum )

    ### LOOPEVAL
    def loopEval( self , data , capt , leave = True , enum = False ):
        if not kld.chk.is_lst( data ) and not kld.chk.is_int( data ):
            data = range( data.num_batches() )
        text = 'Eval {}'.format( capt.upper() )
        return self.loopBar( data , text , leave , enum )

######################################################

    ### DRAW PREV
    def draw_prev( self , data ):
        for i in range( len( data ) ):
            if self.args.eval_draw[i]:
                self.draw_first( data[i] , self.args.eval_capt[i] )

    ### SAVE ITER
    def save_iter( self , stats , epoch ):
        if self.args.train:
            self.saver.scalar( 'epoch' , epoch )
            self.saver.model( 'trained' )
            if self.single_stats:
                self.saver.list( 'stats' , [ epoch ] + stats )
            else:
                for stat , capt in zip( stats , self.args.eval_capt ):
                    if stat is not None: self.saver.list( '%s_stats' % capt , [ epoch ] + stat )

######################################################

    ### PADSTR
    def padstr( self , str ):
        diff = self.width - len( str ) - 6
        if diff > 0: str += ' |' + ' ' * diff
        return '| ' + str + ' |'

    ### EVALUATE ALL
    def evaluate_all( self , data , epoch , extras = None ):

        data = kld.lst.make( data )
        for d in data:
            if d is not None: break
        else: return [ None ] * len( data )

        kld.dsp.print_hline( self.width )
        stats = [ None if data[i] is None else self.evaluate_loop(
                  data[i] , epoch , self.args.eval_capt[i] ,
                                    self.args.eval_draw[i] ) for i in range( len( data ) ) ]
        if extras is not None:
            for extra in kld.lst.make( extras ): extra()

        kld.dsp.print_hline( self.width )
        if self.single_stats:
            print( self.padstr( self.display( 'STATS' , epoch , stats ) ) )
        else:
            for capt , stat in zip( self.args.eval_capt , stats ):
                if stat is not None:
                    print( self.padstr( self.display( capt.upper() , epoch , stat ) ) )

        kld.dsp.print_hline( self.width )
        return stats[0] if len( stats ) == 1 else stats

######################################################
