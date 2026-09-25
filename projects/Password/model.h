#pragma once
#include <cstdarg>
namespace Eloquent {
    namespace ML {
        namespace Port {
            class OneClassSVM {
                public:
                    /**
                    * Predict class for features vector
                    */
                    int predict(float *x) {
                        float kernels[3] = { 0 };
                        kernels[0] = compute_kernel(x,   0.074617385864  , 0.079882621765  , 0.094308137894  , 0.104326248169  , 0.074663639069  , 0.079695463181  , 0.074655056  , 0.069787979126  , 0.208439826965  , 0.330840349197  , 0.100810050964  , 0.135347366333  , 0.125728130341  , 0.135196208954  , 0.155187606812 );
                        kernels[1] = compute_kernel(x,   0.07032251358  , 0.089163541794  , 0.079804182053  , 0.099817037582  , 0.074979543686  , 0.079748153687  , 0.07474064827  , 0.07023024559  , 0.970721721649  , 0.198932886124  , 0.223015069962  , 0.120087385178  , 0.110793113708  , 0.140240907669  , 0.174090385437 );
                        kernels[2] = compute_kernel(x,   0.079397916794  , 0.074820518494  , 0.084446907043  , 0.109075069427  , 0.074933767319  , 0.084512233734  , 0.069758176804  , 0.074508190155  , 0.311408519745  , 0.213238716125  , 0.199148654938  , 0.105741024017  , 0.882658958435  , 0.194230079651  , 0.130650997162 );
                        float decision = -0.994633267832 - ( + kernels[0] * 0.078523997852  + kernels[1] * 0.5  + kernels[2] * 0.421476002148 );

                        return decision > 0 ? 0 : 1;
                    }

                protected:
                    /**
                    * Compute kernel between feature vector and support vector.
                    * Kernel type: rbf
                    */
                    float compute_kernel(float *x, ...) {
                        va_list w;
                        va_start(w, 15);
                        float kernel = 0.0;

                        for (uint16_t i = 0; i < 15; i++) {
                            kernel += pow(x[i] - va_arg(w, double), 2);
                        }

                        return exp(-0.01 * kernel);
                    }
                };
            }
        }
    }