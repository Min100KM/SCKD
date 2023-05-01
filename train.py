import time
from options.train_options import TrainOptions
from data.data_loader import CreateDataLoader
from models.models import create_model
from util.visualizer import Visualizer

opt = TrainOptions().parse()
## SEEDING
import torch
import numpy
import random

torch.manual_seed(opt.seed)
numpy.random.seed(opt.seed)
random.seed(opt.seed)
# torch.backends.cudnn.enabled = False
torch.backends.cudnn.deterministic = True
## SEEDING

#import wandb

#wandb.init(project="CS1325_LightPoseNet_heads_1000_1000_500_32", entity="e-lens-", name="posenet_heads_500_bt32")

data_loader = CreateDataLoader(opt)
dataset = data_loader.load_data()
dataset_size = len(data_loader)
print('#training images = %d' % dataset_size)

model = create_model(opt)
visualizer = Visualizer(opt)
total_steps = 0

for epoch in range(opt.epoch_count, opt.niter + opt.niter_decay + 1):
    epoch_start_time = time.time()
    epoch_iter = 0

    for i, data in enumerate(dataset):
        iter_start_time = time.time()
        visualizer.reset()
        total_steps += opt.batchSize
        epoch_iter += opt.batchSize
        model.set_input(data)
        model.optimize_parameters()     # model.pred_B : [output_xy, output_wpqr] x batch

        # if total_steps % opt.display_freq == 0:
        #     save_result = total_steps % opt.update_html_freq == 0
        #     visualizer.display_current_results(model.get_current_visuals(), epoch, save_result)

        if total_steps % opt.print_freq == 0:
            errors = model.get_current_errors()
            t = (time.time() - iter_start_time) / opt.batchSize
            visualizer.print_current_errors(epoch, epoch_iter, errors, t)

            #for k, v in errors.items():
            #    wandb.log({'%s' % k: v})

            if opt.display_id > 0:
                visualizer.plot_current_errors(epoch, float(epoch_iter) / dataset_size, opt, errors)

        # if total_steps % opt.save_latest_freq == 0:
        #     print('saving the latest model (epoch %d, total_steps %d)' %
        #           (epoch, total_steps))
        #     model.save('latest')

    if epoch % opt.save_epoch_freq == 0:
        print('saving the model at the end of epoch %d, iters %d' %
              (epoch, total_steps))
        model.save('latest')
        model.save(epoch)

    print('End of epoch %d / %d \t Time Taken: %d sec' %
          (epoch, opt.niter + opt.niter_decay, time.time() - epoch_start_time))
    model.update_learning_rate()

#wandb.finish()