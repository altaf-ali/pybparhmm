from __future__ import division
import numpy.matlib
import random


def sample_distparams(F,dist_struct,hyperparams,hyperhyperparams,num_iters):

    numObj = len(dist_struct)
    Ki = np.zeros([1,numObj])
    sum_log_pi_kk = np.zeros([1,numObj])
    sum_log_pi_all = np.zeros([1,numObj])
    for ii in range(0,length(dist_struct)):
        Ki[ii] = np.sum(F[ii,:])
        pi_z_ii = dist_struct[ii]['pi_z'][F[ii,:],F[ii,:]]
        pi_z_ii = pi_z_ii/np.matlib.repmat(np.sum(pi_z_ii,1),[1,pi_z_ii.shape[1]])

        sum_log_pi_kk[ii] = np.sum(np.log(np.diag(pi_z_ii)))
        sum_log_pi_all[ii] = np.sum(np.sum(np.log(pi_z_ii)))
    # Hyperparameters for prior on kappa:
    a_kappa=hyperhyperparams['a_kappa']
    b_kappa=hyperhyperparams['b_kappa']

	# Variance of gamma proposal:
    var_kappa = hyperhyperparams['var_kappa']

	# Hyperparameters for prior on alpha:
    a_alpha=hyperhyperparams['a_alpha']
    b_alpha=hyperhyperparams['b_alpha']

	# Variance of gamma proposal:
    var_alpha = hyperhyperparams['var_alpha']

	# Last value of alpha and kappa:
    alpha0 = hyperparams['alpha0']
    kappa0 = hyperparams['kappa0']
    for nn in range(0,num_iters):
        #%%%%%%% Sample kappa given alpha %%%%%%%
        # (a,b) hyperparameters of gamma prior based on fixed variance and setting
        # mean equal to previous kappa value:
        aa_kappa0 = (kappa0**2)/var_kappa
        bb_kappa0 = kappa0/var_kappa
        
        # Sample a proposed kappa:
        kappa = randgamma(aa_kappa0) / bb_kappa0
        
        # Determine log-likelihood of transition distributions given previous kappa
        # value and proposed kappa value:
        log_diff_f = 0
        for ii in range(0,length(dist_struct)):
            log_diff_f = log_diff_f + Ki[ii]*(gammaln(alpha0*Ki[ii]+kappa)-gammaln(alpha0*Ki[ii]+kappa0))\
                - Ki[ii]*(gammaln(alpha0+kappa)-gammaln(alpha0+kappa0)) + (kappa-kappa0)*sum_log_pi_kk[ii]
        
        # Add in prior probability of previous and proposed kappa values:
        log_diff_f = log_diff_f +  (a_kappa-1)*(log(kappa)-log(kappa0))-(kappa-kappa0)*b_kappa
        
        # (a,b) hyperparameters of gamma prior based on fixed variance and setting
        # mean equal to proposed kappa value:
        aa_kappa = (kappa**2)/var_kappa
        bb_kappa = kappa/var_kappa
        
        # Log accept-reject ratio:
        log_rho = log_diff_f + (gammaln(aa_kappa0) - gammaln(aa_kappa))\
            + (aa_kappa-aa_kappa0-1)*np.log(kappa0) - (aa_kappa0-aa_kappa-1)*np.log(kappa)\
            + (aa_kappa0-aa_kappa)*np.log(var_kappa)
        
        if log_rho==np.inf:
            log_rho = -np.inf
        
        rho = np.exp(log_rho)
        
        if rho>1:
            kappa0 = kappa
        else:
            sample_set = [kappa0,kappa]
            ind = (random.random(1)>(1-rho))
            kappa0 = sample_set[ind]
        
        #%%%%%%% Sample alpha given kappa %%%%%%%
        
        #% (a,b) hyperparameters of gamma prior based on fixed variance and setting
        #% mean equal to previous alpha value:
        aa_alpha0 = (alpha0**2)/var_alpha
        bb_alpha0 = alpha0/var_alpha
        
        # Sample a proposed alpha:
        alpha = randgamma(aa_alpha0) / bb_alpha0;
        
        # Determine log-likelihood of transition distributions given previous alpha
        # value and proposed alpha value:
        log_diff_f = 0;
        for ii in range(0,len(dist_struct)):
            log_diff_f = log_diff_f + Ki[ii]*(gammaln(alpha*Ki[ii]+kappa0)-gammaln(alpha0*Ki[ii]+kappa0))\
                - Ki[ii]*(gammaln(alpha+kappa0)-gammaln(alpha0+kappa0))\
                - Ki[ii]*(Ki[ii]-1)*(gammaln(alpha)-gammaln(alpha0))\
                + (alpha-alpha0)*sum_log_pi_all[ii]
       
        # Add in prior probability of previous and proposed alpha values:
        log_diff_f = log_diff_f + (a_alpha-1)*(log(alpha)-log(alpha0))-(alpha-alpha0)*b_alpha
        
        # (a,b) hyperparameters of gamma prior based on fixed variance and setting
        # mean equal to proposed kappa value:
        aa_alpha = (alpha**2)/var_alpha
        bb_alpha = alpha/var_alpha
        
        # Log accept-reject ratio:
        log_rho = log_diff_f + (gammaln(aa_alpha0) - gammaln(aa_alpha))\
            + (aa_alpha-aa_alpha0-1)*log(alpha0) - (aa_alpha0-aa_alpha-1)*log(alpha)\
            + (aa_alpha0-aa_alpha)*log(var_alpha)
        
        if log_rho == np.inf:
            log_rho = -np.inf
        
        
        rho = np.exp(log_rho)
        
        if rho>1:
            alpha0 = alpha
        else:
            sample_set = [alpha0,alpha]
            ind = (random.random(1)>(1-rho))
            alpha0 = sample_set[ind]

# Write final values:
	hyperparams['alpha0'] = alpha0
	hyperparams['kappa0'] = kappa0
	return hyperparams